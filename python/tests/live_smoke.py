"""The library against a REAL server. Not collected by pytest: run it by hand.

    DIPSAC_BASE_URL=http://127.0.0.1:5051 DIPSAC_API_KEY=dps_... \\
    DIPSAC_FREE_KEY=dps_... python tests/live_smoke.py

The unit tests prove what the library sends to a fake. This proves a real server
takes it: the multipart framing, the Content-Length, the file names, the job
routes, and the error bodies as they really arrive. DIPSAC_API_KEY should be a
key whose plan includes audio, video and GLB; DIPSAC_FREE_KEY (optional) is a
Free key, used to meet the per-second limit for real.

Speech is not here: it needs the GPU service, which a test server does not have.
"""
from __future__ import annotations

import asyncio
import os
import sys
import time
from pathlib import Path

import dipsac
from dipsac import AsyncDipsac, Dipsac, DipsacFile, Job

FIX = Path(__file__).resolve().parents[2] / "fixtures"
passed = failed = 0


def check(name: str, ok: bool, detail: object = "") -> None:
    global passed, failed
    if ok:
        passed += 1
        print(f"  PASS  {name}")
    else:
        failed += 1
        print(f"  FAIL  {name}  -> {detail!r}"[:400])


def attempt(name: str, fn):
    """Run one call; a raise is a failed check, never the end of the run."""
    try:
        return fn()
    except Exception as exc:  # noqa: BLE001
        check(name, False, f"{type(exc).__name__}: {exc}")
        return None


def is_file(x, starts: bytes, ctype: str) -> bool:
    return isinstance(x, DipsacFile) and x.content.startswith(starts) and x.content_type == ctype


client = Dipsac()
print(f"against {client.base_url}")

print("[1] PDF")
out = attempt("merge", lambda: client.pdf.merge([FIX / "doc.pdf", FIX / "doc2.pdf"]))
check("two paths merge into one PDF named by the API", is_file(out, b"%PDF", "application/pdf") and out.filename == "merged.pdf", out)
meta = attempt("metadata", lambda: client.pdf.metadata(out.content if out else b""))
check("the merged file has both documents' pages (3 + 2), read from bare bytes", isinstance(meta, dict) and meta.get("pages") == 5, meta)
out = attempt("split", lambda: client.pdf.split(str(FIX / "doc.pdf"), "1-2"))
check("split by a page range", is_file(out, b"%PDF", "application/pdf"), out)
with open(FIX / "doc.pdf", "rb") as fh:
    out = attempt("rotate", lambda: client.pdf.rotate(fh, degrees=180))
check("an open file is uploaded under its own name", is_file(out, b"%PDF", "application/pdf") and out.filename == "doc-rotated.pdf", out)
out = attempt("convert", lambda: client.pdf.convert(FIX / "doc.pdf", "docx"))
check("PDF to Word answers with a .docx, which the schema calls JSON", isinstance(out, DipsacFile) and out.content[:2] == b"PK" and (out.filename or "").endswith(".docx"), out)
out = attempt("from_office", lambda: client.pdf.from_office(FIX / "letter.docx"))
check("Word to PDF", is_file(out, b"%PDF", "application/pdf"), out)
out = attempt("protect", lambda: client.pdf.protect(FIX / "doc.pdf", "s3cret", allow_printing=False))
check("a boolean reaches the server as it reads one", is_file(out, b"%PDF", "application/pdf"), out)

print("[2] a background job")
job = attempt("compress async", lambda: client.pdf.compress(FIX / "doc.pdf", mode="async"))
check("mode='async' answers with a Job that is queued", isinstance(job, Job) and job.status == "queued" and len(job.id) > 8, job)
if isinstance(job, Job):
    done = attempt("wait", lambda: job.wait(timeout=120, poll_interval=1.0))
    check("wait() ends in the file", is_file(done, b"%PDF", "application/pdf") and job.status == "succeeded", (done, job))
    again = attempt("job by id", lambda: client.job(job.id).wait(timeout=30, poll_interval=1.0))
    check("the same job can be fetched again by its id", isinstance(again, DipsacFile) and again.content == done.content, again)
    status = attempt("jobs.get", lambda: client.jobs.get(job.id))
    check("jobs.get is the API's own status body", isinstance(status, dict) and status.get("status") == "succeeded" and "expires_at" in status, status)

print("[3] images, audio, video")
info = attempt("image.info", lambda: client.image.info(FIX / "photo.png"))
check("image facts as a dict", isinstance(info, dict) and (info.get("width"), info.get("height")) == (320, 200), info)
out = attempt("image.convert", lambda: client.image.convert(FIX / "photo.png", "jpg", quality=80))
check("PNG to JPEG", is_file(out, b"\xff\xd8\xff", "image/jpeg"), out)
out = attempt("image.crop", lambda: client.image.crop(FIX / "photo.png", 10, 10, 50, 40))
check("four required integers in order", isinstance(out, DipsacFile) and out.content.startswith(b"\x89PNG"), out)
out = attempt("image.to_pdf", lambda: client.image.to_pdf([FIX / "photo.png", FIX / "photo.png"]))
check("images into one PDF", is_file(out, b"%PDF", "application/pdf"), out)
out = attempt("audio.convert", lambda: client.audio.convert(FIX / "tone.wav", "mp3"))
check("WAV to MP3", isinstance(out, DipsacFile) and out.content_type == "audio/mpeg" and out.size > 500, out)
out = attempt("video.extract_audio", lambda: client.video.extract_audio(FIX / "clip.mp4"))
check("audio out of a video", isinstance(out, DipsacFile) and out.content_type == "audio/mpeg", out)
job = attempt("video.mute async", lambda: client.video.mute(FIX / "clip.mp4", mode="async"))
out = attempt("video wait", lambda: job.wait(timeout=180, poll_interval=1.0)) if isinstance(job, Job) else None
check("a video job, waited for", isinstance(out, DipsacFile) and out.content_type == "video/mp4", out)

print("[4] JSON in, JSON out")
tags = attempt("seo.meta", lambda: client.seo.meta("A title", "A description", "https://example.com"))
check("meta tags", isinstance(tags, dict) and "<title>A title</title>" in str(tags.get("html")), tags)
hashed = attempt("dev.hash", lambda: client.dev.hash("hunter2", rounds=4))
verdict = attempt("dev.hash_verify", lambda: client.dev.hash_verify("hunter2", (hashed or {}).get("hash", "")))
check("a hash made by one call is verified by the other", isinstance(verdict, dict) and True in verdict.values(), verdict)
limits = attempt("glb.limits", lambda: client.glb.limits())
check("a GET with no parameters", isinstance(limits, dict) and "max_ops" in limits, limits)

print("[5] refusals, as they really arrive")
try:
    Dipsac(api_key="dps_not_a_real_key", max_retries=0).dev.json("{}")
    check("a wrong key is refused", False, "no error")
except dipsac.AuthenticationError as e:
    check("a wrong key is AuthenticationError with the API's code and a request id", (e.status_code, e.code) == (401, "unauthorized") and bool(e.request_id), e)
except Exception as e:  # noqa: BLE001
    check("a wrong key is AuthenticationError", False, repr(e))
try:
    client.pdf.metadata(("notes.txt", b"hello"))
    check("the wrong kind of file is refused", False, "no error")
except dipsac.UnsupportedMediaTypeError as e:
    check("the wrong kind of file names what is accepted", e.accepted == [".pdf"] and ".txt" in e.message, (e.accepted, e.message))
except Exception as e:  # noqa: BLE001
    check("the wrong kind of file is UnsupportedMediaTypeError", False, repr(e))
try:
    client.image.crop(FIX / "photo.png", 10, 10, 0, 0)
    check("an impossible crop is refused", False, "no error")
except dipsac.APIStatusError as e:
    check("an impossible crop is refused with a sentence", e.status_code in (400, 422) and bool(e.message), e)
except Exception as e:  # noqa: BLE001
    check("an impossible crop is an APIStatusError", False, repr(e))
try:
    client.jobs.get("0" * 32)
    check("an unknown job is refused", False, "no error")
except dipsac.NotFoundError as e:
    check("an unknown job is NotFoundError", e.code == "not_found", e)
except Exception as e:  # noqa: BLE001
    check("an unknown job is NotFoundError", False, repr(e))

free_key = os.environ.get("DIPSAC_FREE_KEY")
if free_key:
    print("[6] the per-second limit, met for real with a Free key")
    free = Dipsac(api_key=free_key, max_retries=4)
    blunt = Dipsac(api_key=free_key, max_retries=0)
    time.sleep(1.2)
    refused = 0
    for _ in range(6):
        try:
            blunt.dev.json("{}")
        except dipsac.RateLimitError as e:
            refused += 1
            last = e
    check("FIXTURE: with retries off, a burst of six IS refused -- otherwise the next check proves nothing",
          refused >= 1 and last.retry_after == 1.0 and last.code == "rate_limited", refused)
    time.sleep(1.2)
    started = time.monotonic()
    answers = attempt("burst", lambda: [free.dev.json("{}") for _ in range(6)])
    check("with retries on, the same burst all succeeds, and it took real waiting",
          isinstance(answers, list) and len(answers) == 6 and time.monotonic() - started > 0.9,
          (answers and len(answers), round(time.monotonic() - started, 2)))
    try:
        free.audio.convert(FIX / "tone.wav", "mp3")
        check("a Free key is refused audio", False, "no error")
    except dipsac.PermissionDeniedError as e:
        check("a plan refusal says which plan is needed", (e.current_plan, e.required_plan) == ("free", "pro"), e)
    except Exception as e:  # noqa: BLE001
        check("a plan refusal is PermissionDeniedError", False, repr(e))

print("[7] asyncio")


async def go():
    async with AsyncDipsac() as ac:
        merged = await ac.pdf.merge([FIX / "doc.pdf", FIX / "doc2.pdf"])
        j = await ac.pdf.compress(FIX / "doc.pdf", mode="async")
        return merged, await j.wait(timeout=120, poll_interval=1.0)
res = attempt("async", lambda: asyncio.run(go()))
check("the async client merges and waits on a job", bool(res) and all(is_file(x, b"%PDF", "application/pdf") for x in res), res)

print(f"\nPASSED {passed}  FAILED {failed}")
sys.exit(1 if failed else 0)
