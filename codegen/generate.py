"""Generate both SDKs' resource methods from the API's own OpenAPI schema.

    python codegen/generate.py            # rewrite the generated files
    python codegen/generate.py --check    # fail if they are out of date

One method per operation in openapi/dipsac.openapi.json, for Python (sync and
async) and for TypeScript. The hand-written part of each SDK is the transport:
auth, uploads, errors, retries, jobs. This file is the only place an endpoint is
named, so the two SDKs cannot come to disagree about one.

THREE THINGS THE SCHEMA DOES NOT SAY, AND WHERE THEY COME FROM.

  1. WHAT A CALL RETURNS. The schema lists `application/json` for routes that
     answer with a file (POST /v1/image/convert, every audio and video route),
     so RETURNS below was MEASURED: each /v1 operation was called once on a
     running server and its Content-Type read (2026-10-08). The /ai rows were
     read from the route code and not measured, because the speech box is not
     attached to a test server. At run time the SDK decides by the response's
     own Content-Type, so a wrong row here is a wrong type hint and not a crash.
  2. A NAME for the method. Derived from the path; NAMES holds the ones a path
     cannot give (two methods on one path, a path that ends in a parameter).
     Two operations landing on one name stop the generator.
  3. WHICH FIELDS ARE NOT FOR AN SDK. `turnstile_token` is a browser challenge
     and the `access_token` cookie is the website's session; neither can be used
     with an API key.

A NEW OPERATION IN THE SCHEMA WITH NO ROW IN RETURNS STOPS THE GENERATOR, on
purpose: the alternative is a method whose return type nobody checked.
"""
from __future__ import annotations

import json
import keyword
import re
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = ROOT / "openapi" / "dipsac.openapi.json"
PY_OUT = ROOT / "python" / "src" / "dipsac" / "_resources.py"
TS_OUT = ROOT / "js" / "src" / "resources.ts"

# "METHOD path" -> method name, where the path alone cannot name it.
NAMES = {
    "GET /v1/jobs/{job_id}": "get",
    "GET /v1/jobs/{job_id}/result": "result",
    "GET /ai/voices/builtin": "builtin_voices",
    "POST /ai/transcribe/video": "transcribe_video",
    "GET /ai/jobs/{job_id}": "job",
    "GET /ai/library": "library",
    "GET /ai/library/{gen_id}": "library_item",
    "DELETE /ai/library/{gen_id}": "delete_library_item",
    "GET /ai/library/{gen_id}/audio": "library_audio",
    "GET /ai/voices": "voices",
    "POST /ai/voices": "register_voice",
    "DELETE /ai/voices/{voice_id}": "delete_voice",
}

# What each operation answers with on success: "json", "file" or "any".
# An operation that takes `mode` or `async` may answer with a Job instead.
RETURNS = {
    # measured on a running server, 2026-10-08
    "POST /v1/pdf/merge": "file", "POST /v1/pdf/split": "file", "POST /v1/pdf/delete-pages": "file",
    "POST /v1/pdf/rotate": "file", "POST /v1/pdf/compress": "file", "POST /v1/pdf/convert": "file",
    "POST /v1/pdf/from-office": "file", "POST /v1/pdf/protect": "file", "POST /v1/pdf/unlock": "file",
    "POST /v1/pdf/watermark": "file", "POST /v1/pdf/metadata": "json",
    "POST /v1/image/convert": "file", "POST /v1/image/compress": "file", "POST /v1/image/resize": "file",
    "POST /v1/image/crop": "file", "POST /v1/image/remove-background": "file", "POST /v1/image/to-pdf": "file",
    "POST /v1/image/info": "json",
    "POST /v1/audio/convert": "file", "POST /v1/audio/normalize": "file", "POST /v1/audio/merge": "file",
    "POST /v1/video/convert": "file", "POST /v1/video/extract-audio": "file", "POST /v1/video/cut": "file",
    "POST /v1/video/resize": "file", "POST /v1/video/mute": "file",
    "POST /v1/seo/meta": "json", "POST /v1/dev/hash": "json", "POST /v1/dev/json": "json",
    "GET /v1/glb/limits": "json",
    "GET /v1/jobs/{job_id}": "json", "GET /v1/jobs/{job_id}/result": "file",
    # read from the route code, not measured
    "GET /v1/seo/ssl": "json", "GET /v1/seo/redirects": "json", "GET /v1/seo/whois": "json",
    "GET /v1/seo/domain-age": "json", "GET /v1/seo/canonical": "json", "POST /v1/dev/hash/verify": "json",
    "POST /v1/glb/inspect": "json", "POST /v1/glb/plan": "json", "POST /v1/glb/image": "any",
    "GET /ai/status": "json", "GET /ai/pricing": "json", "GET /ai/voices/builtin": "json",
    "POST /ai/transcribe": "json", "POST /ai/transcribe/video": "json", "POST /ai/subtitles": "file",
    "POST /ai/speak": "file", "GET /ai/jobs/{job_id}": "json", "GET /ai/library": "json",
    "GET /ai/library/{gen_id}": "json", "DELETE /ai/library/{gen_id}": "json",
    "GET /ai/library/{gen_id}/audio": "file", "GET /ai/voices": "json", "POST /ai/voices": "json",
    "DELETE /ai/voices/{voice_id}": "json",
}

HIDDEN = {"turnstile_token"}                               # in every operation
HIDDEN_FOR = {"GET /ai/library/{gen_id}/audio": {"fmt"}}    # an alias of `format`
RENAMED = {"async": "background"}                          # wire name -> SDK name

RESOURCE_DOCS = {
    "pdf": "PDF tools: merge, split, compress, convert, protect, watermark.",
    "image": "Image tools: convert, compress, resize, crop, remove a background.",
    "audio": "Audio tools: convert, normalise loudness, join files. Needs the Pro plan.",
    "video": "Video tools: convert, trim, resize, mute, pull the audio out. Needs the Pro plan.",
    "seo": "SEO checks: meta tags, TLS certificate, redirects, WHOIS, canonical.",
    "dev": "Developer utilities: bcrypt hashing, JSON validation and formatting.",
    "glb": "3D model (.glb) inspection and editing plans. Needs the Enterprise plan.",
    "jobs": "Status and result of work submitted with mode=\"async\".",
    "ai": "AI Voice Studio: text to speech, transcription, subtitles, cloned voices.",
}

# The /ai routes carry no customer-facing text in the schema, so theirs is here.
AI_DOCS = {
    "status": "What this account may do in the AI Voice Studio, and what it has used.",
    "pricing": "The studio's plans, limits and prices.",
    "builtin_voices": "The built-in voices, optionally for one language.",
    "transcribe": "Turn an audio file into text.",
    "transcribe_video": "Turn the speech in a video file into text.",
    "subtitles": "Make a subtitle file (SRT or VTT) from audio or video.",
    "speak": "Turn text into speech. With background=True it returns a Job to wait on, "
             "which is the way to synthesise long text.",
    "job": "The state of a background speech job, as the API reports it.",
    "library": "List what this account has generated.",
    "library_item": "One generation from the library, with its details.",
    "delete_library_item": "Delete one generation from the library.",
    "library_audio": "Download the audio of one generation.",
    "voices": "The cloned voices this account has registered.",
    "register_voice": "Register a cloned voice from a recording of the speaker.",
    "delete_voice": "Erase a cloned voice.",
}
AI_PARAM_DOCS = {
    "file": "The audio or video file",
    "language": "Language code, e.g. en, hi",
    "diarize": "Label who is speaking",
    "translate": "Translate the transcript into English",
    "fmt": "Output format",
    "text": "The text to speak",
    "voice": "A built-in voice, by name (see builtin_voices)",
    "cloned_voice": "A cloned voice you registered, by name",
    "speed": "Speaking rate; 1.0 is normal",
    "style": "Speaking style, where the voice supports one",
    "background": "Return a Job at once and synthesise in the background",
    "kind": "Only this kind of generation",
    "limit": "How many to return",
    "before_id": "Return items older than this id",
    "search": "Only items whose text contains this",
    "format": "Download format, e.g. mp3",
    "name": "A name for the voice",
    "consent": "The speaker's consent statement",
}


# ── reading the schema ──────────────────────────────────────────────────────
def load():
    doc = json.loads(SCHEMA.read_text(encoding="utf-8"))
    comps = doc.get("components", {}).get("schemas", {})

    def deref(s):
        while s and "$ref" in s:
            s = comps[s["$ref"].split("/")[-1]]
        return s or {}

    def kind_of(s):
        """(kind, nullable, enum) with kind in str int float bool file files any."""
        s = deref(s)
        if "anyOf" in s:
            parts = [deref(x) for x in s["anyOf"]]
            real = [x for x in parts if x.get("type") != "null"]
            k, _, e = kind_of(real[0]) if len(real) == 1 else ("any", False, None)
            return k, len(real) != len(parts), e
        t = s.get("type")
        if t == "array":
            inner, _, _ = kind_of(s.get("items", {}))
            return ("files" if inner == "file" else "any"), False, None
        if t == "string" and (s.get("format") == "binary" or "contentMediaType" in s):
            return "file", False, None
        if t == "string":
            return "str", False, s.get("enum")
        return {"integer": "int", "number": "float", "boolean": "bool"}.get(t, "any"), False, None

    ops = []
    for path, item in doc["paths"].items():
        for method, op in item.items():
            if method not in ("get", "post", "put", "patch", "delete"):
                continue
            key = f"{method.upper()} {path}"
            segs = [s for s in path.strip("/").split("/")]
            resource = segs[1] if segs[0] == "v1" else segs[0]
            tail = [s for s in (segs[2:] if segs[0] == "v1" else segs[1:]) if not s.startswith("{")]
            name = NAMES.get(key) or "_".join(tail).replace("-", "_")
            if not name:
                sys.exit(f"{key}: the path gives no method name; add one to NAMES")
            if key not in RETURNS:
                sys.exit(f"{key}: no row in RETURNS. Call it once, read its Content-Type, and add it.")
            hidden = HIDDEN | HIDDEN_FOR.get(key, set())

            def param(wire, schema, required, where, description=None):
                k, nullable, enum = kind_of(schema)
                sdk = RENAMED.get(wire, wire)
                s = deref(schema)
                doc_ = description or s.get("description") or (AI_PARAM_DOCS.get(sdk) if resource == "ai" else None)
                return {"wire": wire, "name": sdk, "kind": k, "required": bool(required), "enum": enum,
                        "where": where, "doc": doc_, "default": s.get("default") if "default" in s else None,
                        "has_default": "default" in s}

            params = []
            for p in op.get("parameters", []):
                if p["in"] in ("cookie", "header") or p["name"] in hidden:
                    continue
                params.append(param(p["name"], p.get("schema", {}), p.get("required"), p["in"], p.get("description")))
            body_kind = None
            content = op.get("requestBody", {}).get("content", {})
            for ctype, spec in content.items():
                body_kind = {"multipart/form-data": "multipart", "application/x-www-form-urlencoded": "form",
                             "application/json": "json"}.get(ctype)
                if body_kind is None:
                    sys.exit(f"{key}: a request body of {ctype}, which the SDKs do not send")
                sch = deref(spec.get("schema", {}))
                req = set(sch.get("required", []))
                for wire, fs in (sch.get("properties") or {}).items():
                    if wire in hidden:
                        continue
                    params.append(param(wire, fs, wire in req, "body"))
            desc = (op.get("description") or "").strip()
            if resource == "ai":
                summary, extra = AI_DOCS[name], ""
            else:
                summary = (op.get("summary") or name).strip().rstrip(".") + "."
                extra = desc.split("\n\n")[0].strip() if desc else ""
            ops.append({"key": key, "method": method.upper(), "path": path, "resource": resource, "name": name,
                        "summary": summary, "extra": extra, "params": params, "body": body_kind,
                        "returns": RETURNS[key],
                        "job": any(p["wire"] in ("mode", "async") for p in params)})
    stale = set(RETURNS) - {o["key"] for o in ops}
    if stale:
        sys.exit("RETURNS names operations the schema no longer has: " + ", ".join(sorted(stale)))
    seen = {}
    for o in ops:
        k = (o["resource"], o["name"])
        if k in seen:
            sys.exit(f"{o['key']} and {seen[k]} both become {o['resource']}.{o['name']}; add one to NAMES")
        seen[k] = o["key"]
    order = ["pdf", "image", "audio", "video", "seo", "dev", "glb", "jobs", "ai"]
    resources = sorted({o["resource"] for o in ops}, key=lambda r: (order.index(r) if r in order else 99, r))
    unknown = [r for r in resources if r not in RESOURCE_DOCS]
    if unknown:
        sys.exit("a resource with no entry in RESOURCE_DOCS: " + ", ".join(unknown))
    return doc, resources, ops


def ordered(params):
    path = [p for p in params if p["where"] == "path"]
    req = [p for p in params if p["where"] != "path" and p["required"]]
    opt = [p for p in params if p["where"] != "path" and not p["required"]]
    return path, req, opt


def doc_default(p):
    return f" (server default: {p['default']!r})" if p["has_default"] and p["default"] not in (None, "") else ""


# ── Python ───────────────────────────────────────────────────────────────────
PY_TYPES = {"str": "str", "int": "int", "float": "float", "bool": "bool", "file": "FileInput",
            "files": "Sequence[FileInput]", "any": "Any"}


def py_name(n):
    return n + "_" if keyword.iskeyword(n) else n


def py_type(p):
    if p["enum"]:
        return "Literal[" + ", ".join(repr(e) for e in p["enum"]) + "]"
    return PY_TYPES[p["kind"]]


def py_return(o, job):
    base = {"json": "Dict[str, Any]", "file": "DipsacFile", "any": "Any"}[o["returns"]]
    return f"Union[{base}, {job}]" if o["job"] and base != "Any" else base


def py_method(o, is_async):
    path, req, opt = ordered(o["params"])
    sig = ["self"] + [f"{py_name(p['name'])}: {py_type(p)}" for p in path + req]
    sig.append("*")
    sig += [f"{py_name(p['name'])}: Optional[{py_type(p)}] = None" for p in opt]
    sig.append("timeout: Optional[float] = None")
    ret = py_return(o, "AsyncJob" if is_async else "Job")
    lines = [f"    {'async ' if is_async else ''}def {py_name(o['name'])}(", ]
    lines += [f"        {s}," for s in sig]
    lines.append(f"    ) -> {ret}:")
    doc = [o["summary"]]
    if o["extra"]:
        doc += ["", *textwrap.wrap(o["extra"], 84)]
    documented = [p for p in path + req + opt if p["doc"]]
    if documented:
        doc += ["", "Args:"]
        for p in documented:
            text = f"{py_name(p['name'])}: {p['doc'].strip().rstrip('.')}{doc_default(p)}"
            wrapped = textwrap.wrap(text, 80)
            doc.append("    " + wrapped[0])
            doc += ["        " + w for w in wrapped[1:]]
    if o["job"]:
        doc += ["", "Returns a Job instead of the result when the work is sent to the", "background; call its wait() for the result."]
    lines.append('        """' + doc[0])
    lines += [("        " + d).rstrip() for d in doc[1:]]
    lines.append('        """')
    url = re.sub(r"\{(\w+)\}", lambda m: "{_seg(" + py_name(m.group(1)) + ")}", o["path"])
    call = [f'"{o["method"]}"', ('f"' if "{" in url else '"') + url + '"']
    groups = {"query": [p for p in o["params"] if p["where"] == "query"],
              "files": [p for p in o["params"] if p["where"] == "body" and p["kind"] in ("file", "files")],
              "fields": [p for p in o["params"] if p["where"] == "body" and p["kind"] not in ("file", "files")]}

    def mapping(ps):
        return "{" + ", ".join(f'"{p["wire"]}": {py_name(p["name"])}' for p in ps) + "}"
    if groups["query"]:
        call.append("query=" + mapping(groups["query"]))
    if groups["files"]:
        call.append("files=" + mapping(groups["files"]))
    if groups["fields"]:
        call.append(("json=" if o["body"] == "json" else "form=") + mapping(groups["fields"]))
    if o["body"] == "multipart":
        call.append("multipart=True")
    call.append("timeout=timeout")
    lines.append(f"        return {'await ' if is_async else ''}self._client._request(")
    lines += [f"            {c}," for c in call]
    lines.append("        )")
    return "\n".join(lines)


def py_class(resource, ops, is_async):
    name = ("Async" if is_async else "") + resource.capitalize()
    out = [f"class {name}(_{'Async' if is_async else ''}Resource):", f'    """{RESOURCE_DOCS[resource]}"""', ""]
    out.append("\n\n".join(py_method(o, is_async) for o in ops))
    return "\n".join(out)


def render_python(resources, ops):
    head = textwrap.dedent('''\
        """The API's operations, one method each. GENERATED: do not edit.

        Written by codegen/generate.py from openapi/dipsac.openapi.json. To change
        a method, change the schema snapshot (or the tables in the generator) and
        run it again.
        """
        from __future__ import annotations

        from typing import TYPE_CHECKING, Any, Dict, Literal, Optional, Sequence, Union
        from urllib.parse import quote

        from ._files import FileInput
        from ._models import AsyncJob, DipsacFile, Job

        if TYPE_CHECKING:
            from ._client import AsyncDipsac, Dipsac


        def _seg(value: Any) -> str:
            """One path segment, escaped."""
            return quote(str(value), safe="")


        class _Resource:
            def __init__(self, client: "Dipsac") -> None:
                self._client = client


        class _AsyncResource:
            def __init__(self, client: "AsyncDipsac") -> None:
                self._client = client
        ''')
    blocks = [head]
    for is_async in (False, True):
        for r in resources:
            blocks.append(py_class(r, [o for o in ops if o["resource"] == r], is_async))
    table = ["RESOURCES = {"] + [f'    "{r}": ({r.capitalize()}, Async{r.capitalize()}),' for r in resources] + ["}"]
    listing = ["OPERATIONS = ("] + [f'    ("{o["method"]}", "{o["path"]}", "{o["resource"]}", "{py_name(o["name"])}"),' for o in ops] + [")"]
    blocks += ["\n".join(table), "\n".join(listing)]
    return "\n\n\n".join(blocks) + "\n"


# ── TypeScript ───────────────────────────────────────────────────────────────
TS_TYPES = {"str": "string", "int": "number", "float": "number", "bool": "boolean", "file": "FileInput",
            "files": "FileInput[]", "any": "unknown"}


def camel(n):
    parts = n.split("_")
    return parts[0] + "".join(x.capitalize() for x in parts[1:])


def pascal(n):
    return "".join(x.capitalize() for x in n.split("_"))


def ts_type(p):
    if p["enum"]:
        return " | ".join(json.dumps(e) for e in p["enum"])
    return TS_TYPES[p["kind"]]


def ts_return(o):
    base = {"json": "JsonObject", "file": "DipsacFile", "any": "unknown"}[o["returns"]]
    return f"{base} | Job" if o["job"] and base != "unknown" else base


def ts_method(o, iface):
    path, req, opt = ordered(o["params"])
    rest = req + opt
    args = [f"{camel(p['name'])}: {ts_type(p)}" for p in path]
    if rest:
        args.append(f"params: {iface}" + ("" if req else " = {}"))
    args.append("options?: RequestOptions")
    doc = ["  /**", f"   * {o['summary']}"]
    if o["extra"]:
        doc += ["   *"] + ["   * " + w for w in textwrap.wrap(o["extra"], 84)]
    if o["job"]:
        doc += ["   *", "   * Resolves to a Job instead of the result when the work is sent to the",
                "   * background; await its wait() for the result."]
    doc.append("   */")
    url = re.sub(r"\{(\w+)\}", lambda m: "${seg(" + camel(m.group(1)) + ")}", o["path"])
    url = ("`" + url + "`") if "${" in url else json.dumps(url)
    spec = [f'method: "{o["method"]}"', f"path: {url}"]

    def mapping(ps):
        return "{ " + ", ".join(f'{json.dumps(p["wire"]) if not re.fullmatch(r"[A-Za-z_]\w*", p["wire"]) else p["wire"]}: params.{camel(p["name"])}' for p in ps) + " }"
    q = [p for p in o["params"] if p["where"] == "query"]
    fl = [p for p in o["params"] if p["where"] == "body" and p["kind"] in ("file", "files")]
    fd = [p for p in o["params"] if p["where"] == "body" and p["kind"] not in ("file", "files")]
    if q:
        spec.append("query: " + mapping(q))
    if fl:
        spec.append("files: " + mapping(fl))
    if fd:
        spec.append(("json: " if o["body"] == "json" else "form: ") + mapping(fd))
    if o["body"] == "multipart":
        spec.append("multipart: true")
    ret = ts_return(o)
    body = [f"  {camel(o['name'])}({', '.join(args)}): Promise<{ret}> {{",
            f"    return this.client.request({{ {', '.join(spec)} }}, options) as Promise<{ret}>;", "  }"]
    return "\n".join(doc + body)


def ts_interface(o, iface):
    _, req, opt = ordered(o["params"])
    if not (req + opt):
        return None
    lines = [f"export interface {iface} {{"]
    for p in req + opt:
        if p["doc"]:
            lines.append(f"  /** {p['doc'].strip().rstrip('.')}{doc_default(p)} */".replace("*/ */", "*/"))
        lines.append(f"  {camel(p['name'])}{'' if p['required'] else '?'}: {ts_type(p)};")
    lines.append("}")
    return "\n".join(lines)


def render_typescript(resources, ops):
    head = textwrap.dedent('''\
        // The API's operations, one method each. GENERATED: do not edit.
        //
        // Written by codegen/generate.py from openapi/dipsac.openapi.json. To change a
        // method, change the schema snapshot (or the tables in the generator) and run
        // it again.
        import type { Dipsac, RequestOptions } from "./client.js";
        import type { FileInput } from "./files.js";
        import type { DipsacFile, Job, JsonObject } from "./models.js";

        const seg = (value: string | number): string => encodeURIComponent(String(value));

        class Resource {
          constructor(protected readonly client: Dipsac) {}
        }
        ''')
    blocks = [head.rstrip("\n")]
    for r in resources:
        rops = [o for o in ops if o["resource"] == r]
        ifaces, methods = [], []
        for o in rops:
            iface = f"{r.capitalize()}{pascal(o['name'])}Params"
            i = ts_interface(o, iface)
            if i:
                ifaces.append(i)
            methods.append(ts_method(o, iface))
        blocks.append("\n\n".join(ifaces + [f"/** {RESOURCE_DOCS[r]} */\nexport class {r.capitalize()} extends Resource {{\n" + "\n\n".join(methods) + "\n}"]))
    listing = ["export const OPERATIONS: ReadonlyArray<readonly [string, string, string, string]> = ["]
    listing += [f'  ["{o["method"]}", "{o["path"]}", "{o["resource"]}", "{camel(o["name"])}"],' for o in ops] + ["];"]
    blocks.append("\n".join(listing))
    return "\n\n".join(blocks) + "\n"


def main():
    _, resources, ops = load()
    outputs = {PY_OUT: render_python(resources, ops), TS_OUT: render_typescript(resources, ops)}
    if "--check" in sys.argv:
        stale = [str(p.relative_to(ROOT)) for p, text in outputs.items()
                 if not p.exists() or p.read_text(encoding="utf-8") != text]
        if stale:
            sys.exit("out of date, run codegen/generate.py: " + ", ".join(stale))
        print(f"{len(ops)} operations in {len(resources)} resources; generated files are up to date")
        return
    for p, text in outputs.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8", newline="\n")
    print(f"{len(ops)} operations in {len(resources)} resources written to "
          + " and ".join(str(p.relative_to(ROOT)) for p in outputs))


if __name__ == "__main__":
    main()
