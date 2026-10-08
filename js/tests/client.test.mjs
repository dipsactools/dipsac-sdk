// The transport, against a local HTTP server that records what it was sent.
// A real socket and the real fetch, so the framing is what a server would see.
import assert from "node:assert/strict";
import { File } from "node:buffer"; // a global only from Node 20
import { mkdtemp, readFile, writeFile } from "node:fs/promises";
import http from "node:http";
import { createRequire } from "node:module";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { after, before, beforeEach, test as rawTest } from "node:test";

// EVERY TEST HAS A CEILING. Break the rule that the monthly limit is not slept
// through and the library sleeps for a day: without a ceiling that is a run that
// never ends, which reads as "still going" and never as red.
const test = (name, fn) => rawTest(name, { timeout: 15_000 }, fn);

import * as dipsac from "../dist/esm/index.js";

const { Dipsac, DipsacFile, Job } = dipsac;
const PDF = Buffer.from("%PDF-1.7\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF\n");

let server, base, answers, seen;

before(async () => {
  server = http.createServer((req, res) => {
    const chunks = [];
    req.on("data", (c) => chunks.push(c));
    req.on("end", () => {
      seen.push({ method: req.method, url: req.url, headers: req.headers, body: Buffer.concat(chunks) });
      const a = answers.shift();
      if (!a) {
        res.writeHead(599, { "content-type": "text/plain" }).end("an unexpected request");
        return;
      }
      if (a.hangup) return req.socket.destroy();
      res.writeHead(a.status ?? 200, a.headers ?? {}).end(a.body ?? "");
    });
  });
  await new Promise((r) => server.listen(0, "127.0.0.1", r));
  base = `http://127.0.0.1:${server.address().port}`;
});
after(() => server.close());
beforeEach(() => {
  answers = [];
  seen = [];
});

const j = (body = {}, status = 200, headers = {}) => ({
  status,
  headers: { "content-type": "application/json", ...headers },
  body: JSON.stringify(body),
});
const file = (body = PDF, type = "application/pdf", name = "out.pdf", headers = {}) => ({
  headers: { "content-type": type, "content-disposition": `attachment; filename="${name}"`, ...headers },
  body,
});
const client = (opts = {}) => new Dipsac({ apiKey: "dps_test", baseUrl: base, ...opts });

// ── who we say we are ───────────────────────────────────────────────────────
test("the key goes in X-API-Key and the library names itself", async () => {
  answers.push(j({ ok: true }));
  await client().dev.json({ content: "{}" });
  assert.equal(seen[0].headers["x-api-key"], "dps_test");
  assert.equal(seen[0].headers["user-agent"], `dipsac-node/${dipsac.VERSION}`);
  assert.equal(seen[0].url, "/v1/dev/json");
});

test("no key anywhere is refused before any request", () => {
  const saved = process.env.DIPSAC_API_KEY;
  delete process.env.DIPSAC_API_KEY;
  try {
    assert.throws(() => new Dipsac(), /No API key/);
  } finally {
    if (saved !== undefined) process.env.DIPSAC_API_KEY = saved;
  }
});

test("the version in the code is the version in package.json", async () => {
  const pkg = JSON.parse(await readFile(new URL("../package.json", import.meta.url), "utf8"));
  assert.equal(dipsac.VERSION, pkg.version);
});

// ── what is sent ────────────────────────────────────────────────────────────
test("a JSON body leaves out what the caller left out", async () => {
  answers.push(j());
  await client().dev.json({ content: '{"a":1}', sortKeys: true });
  assert.deepEqual(JSON.parse(seen[0].body.toString()), { content: '{"a":1}', sort_keys: true });
  assert.equal(seen[0].headers["content-type"], "application/json");
});

test("query parameters for a GET", async () => {
  answers.push(j());
  await client().seo.ssl({ url: "example.com" });
  assert.equal(seen[0].method, "GET");
  assert.equal(seen[0].url, "/v1/seo/ssl?url=example.com");
});

test("an upload is multipart WITH A LENGTH, a name, and string fields", async () => {
  const dir = await mkdtemp(join(tmpdir(), "dipsac-js-"));
  const path = join(dir, "report.pdf");
  await writeFile(path, PDF);
  answers.push(file());
  await client().pdf.compress({ file: path, preset: "screen", removeMetadata: false });
  const sent = seen[0];
  assert.match(sent.headers["content-type"], /^multipart\/form-data; boundary=/);
  // The API answers 411 to an upload with no length, so chunked would be a refusal.
  assert.equal(Number(sent.headers["content-length"]), sent.body.length);
  assert.equal(sent.headers["transfer-encoding"], undefined);
  const body = sent.body.toString("latin1");
  assert.ok(body.includes('name="file"; filename="report.pdf"') && sent.body.includes(PDF));
  assert.match(body, /name="preset"\r\n\r\nscreen/);
  assert.match(body, /name="remove_metadata"\r\n\r\nfalse/);
  assert.ok(!body.includes('name="mode"'), "left out, so the server's default applies");
});

test("several files go under one repeated name, in order", async () => {
  answers.push(file());
  await client().pdf.merge({ files: [{ data: PDF, filename: "first.pdf" }, { data: PDF, filename: "second.pdf" }] });
  const body = seen[0].body.toString("latin1");
  const a = body.indexOf('filename="first.pdf"');
  const b = body.indexOf('filename="second.pdf"');
  assert.ok(a > 0 && b > a);
  assert.equal(body.split('name="files"').length - 1, 2);
});

test("bare bytes are named by what they are, and a File keeps its own name", async () => {
  answers.push(j(), j(), j());
  const c = client();
  await c.pdf.metadata({ file: new Uint8Array(PDF) });
  await c.image.info({ file: new Uint8Array([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 0, 0, 0, 0]) });
  await c.pdf.metadata({ file: new File([PDF], "scan.pdf") });
  assert.ok(seen[0].body.toString("latin1").includes('filename="file.pdf"'));
  assert.ok(seen[1].body.toString("latin1").includes('filename="file.png"'));
  assert.ok(seen[2].body.toString("latin1").includes('filename="scan.pdf"'));
});

test("speech is a form, and background travels as async", async () => {
  answers.push(file(Buffer.from("RIFFxxxxWAVE"), "audio/wav", "speech.wav"));
  await client().ai.speak({ text: "Namaste", language: "hi", speed: 1.1 });
  assert.match(seen[0].headers["content-type"], /^application\/x-www-form-urlencoded/);
  assert.deepEqual(Object.fromEntries(new URLSearchParams(seen[0].body.toString())), { text: "Namaste", language: "hi", speed: "1.1" });
  answers.push(j({ job_id: "j1", status: "queued", poll: "/ai/jobs/j1" }, 202));
  const job = await client().ai.speak({ text: "long text", background: true });
  assert.ok(job instanceof Job);
  assert.equal(new URLSearchParams(seen[1].body.toString()).get("async"), "true");
});

test("a path parameter is escaped", async () => {
  answers.push(j());
  await client().jobs.get("a/b c");
  assert.equal(seen[0].url, "/v1/jobs/a%2Fb%20c");
});

// ── what comes back ─────────────────────────────────────────────────────────
test("JSON comes back as an object, a file as a DipsacFile that can be saved", async () => {
  answers.push(j({ width: 320 }), file(PDF, "application/pdf", "merged.pdf", { "x-original-size": "856" }));
  const c = client();
  assert.deepEqual(await c.image.info({ file: new Uint8Array(PDF) }), { width: 320 });
  const out = await c.pdf.merge({ files: [new Uint8Array(PDF), new Uint8Array(PDF)] });
  assert.ok(out instanceof DipsacFile);
  assert.deepEqual([out.contentType, out.filename, out.size], ["application/pdf", "merged.pdf", PDF.length]);
  assert.equal(out.headers["x-original-size"], "856");
  const dir = await mkdtemp(join(tmpdir(), "dipsac-js-"));
  const where = await out.save(dir);
  assert.equal(where, join(dir, "merged.pdf"));
  assert.deepEqual(await readFile(where), PDF);
});

test("a name that is not ASCII is read from the UTF-8 form, and cannot leave its folder", async () => {
  answers.push({
    headers: {
      "content-type": "application/pdf",
      "content-disposition": "attachment; filename=\"document_signed.pdf\"; filename*=UTF-8''%E0%A4%85%E0%A4%A8%E0%A5%81%E0%A4%AC%E0%A4%82%E0%A4%A7_signed.pdf",
    },
    body: PDF,
  });
  answers.push({ headers: { "content-type": "application/pdf", "content-disposition": 'attachment; filename="../../evil.pdf"' }, body: PDF });
  const c = client();
  assert.equal((await c.pdf.unlock({ file: new Uint8Array(PDF) })).filename, "अनुबंध_signed.pdf");
  assert.equal((await c.pdf.unlock({ file: new Uint8Array(PDF) })).filename, "evil.pdf");
});

test("subtitles come back as text", async () => {
  answers.push({ headers: { "content-type": "text/plain; charset=utf-8" }, body: Buffer.from("1\n00:00:00,000 --> 00:00:01,000\nनमस्ते\n") });
  const out = await client().ai.subtitles({ file: { data: new Uint8Array([0x49, 0x44, 0x33]), filename: "a.mp3" } });
  assert.ok(out.text().includes("नमस्ते"));
});

// ── errors ──────────────────────────────────────────────────────────────────
test("each status is its own error, carrying the API's words", async () => {
  const table = [
    [400, dipsac.BadRequestError], [401, dipsac.AuthenticationError], [402, dipsac.PaymentRequiredError],
    [403, dipsac.PermissionDeniedError], [404, dipsac.NotFoundError], [409, dipsac.ConflictError],
    [413, dipsac.PayloadTooLargeError], [415, dipsac.UnsupportedMediaTypeError],
    [422, dipsac.UnprocessableEntityError], [500, dipsac.InternalServerError], [418, dipsac.APIStatusError],
  ];
  for (const [status, Cls] of table) {
    const body = { error: "some_code", message: "A sentence.", request_id: "rid1", detail: "A sentence." };
    answers.push(j(body, status));
    await assert.rejects(client().dev.json({ content: "{}" }), (e) => {
      assert.equal(e.constructor, Cls, `status ${status}`);
      assert.deepEqual([e.status, e.code, e.message, e.requestId], [status, "some_code", "A sentence.", "rid1"]);
      assert.deepEqual(e.body, body);
      assert.ok(e instanceof dipsac.DipsacError && e instanceof Error);
      return true;
    });
  }
});

test("the extra fields of three refusals are readable", async () => {
  answers.push(j({ error: "upgrade_required", message: "m", current_plan: "free", required_plan: "pro" }, 403));
  await assert.rejects(client().audio.merge({ files: [new Uint8Array(PDF)] }), (e) => e.currentPlan === "free" && e.requiredPlan === "pro");
  answers.push(j({ error: "unsupported_media_type", message: "m", accepted: [".pdf"] }, 415));
  await assert.rejects(client().pdf.metadata({ file: { data: new Uint8Array([1]), filename: "a.txt" } }), (e) => e.accepted[0] === ".pdf");
  answers.push(j({ error: "invalid_request", message: "m", fields: [{ field: "content" }] }, 422));
  await assert.rejects(client().dev.json({ content: "" }), (e) => e.fields[0].field === "content");
});

test("an error that is not JSON still says something", async () => {
  answers.push({ status: 502, headers: { "content-type": "text/html", "x-request-id": "edge1" }, body: "<html>Bad Gateway</html>" });
  await assert.rejects(client({ maxRetries: 0 }).dev.json({ content: "{}" }), (e) =>
    e instanceof dipsac.InternalServerError && e.message.includes("Bad Gateway") && e.requestId === "edge1");
});

// ── retries ─────────────────────────────────────────────────────────────────
test("the per-second limit is waited out and the request sent again", async () => {
  answers.push(j({ error: "rate_limited", message: "2 requests/second" }, 429, { "retry-after": "0.3" }), j({ valid: true }));
  const started = Date.now();
  assert.deepEqual(await client().dev.json({ content: "{}" }), { valid: true });
  assert.equal(seen.length, 2);
  assert.ok(Date.now() - started >= 280, "it waited what it was asked to");
});

test("the monthly limit is thrown at once and not slept through", async () => {
  answers.push(j({ error: "rate_limited", message: "Monthly request limit of 500 reached" }, 429, { "retry-after": "86400" }));
  const started = Date.now();
  await assert.rejects(client().dev.json({ content: "{}" }), (e) => e instanceof dipsac.RateLimitError && e.retryAfter === 86400);
  assert.equal(seen.length, 1);
  assert.ok(Date.now() - started < 2000);
});

test("a POST that failed on the server is not sent twice; a GET is tried again", async () => {
  answers.push(j({ error: "service_unavailable", message: "m" }, 503));
  await assert.rejects(client().ai.speak({ text: "paid for per call" }), dipsac.InternalServerError);
  assert.equal(seen.length, 1);
  answers.push(j({ error: "x", message: "m" }, 503), j({ status: "running" }));
  assert.deepEqual(await client().jobs.get("j1"), { status: "running" });
  assert.equal(seen.length, 3);
});

test("a POST whose connection broke is not sent twice", async () => {
  answers.push({ hangup: true });
  await assert.rejects(client().dev.json({ content: "{}" }), dipsac.APIConnectionError);
  assert.equal(seen.length, 1);
});

test("a call that outlasts its timeout is a timeout error", async () => {
  const slow = http.createServer(() => {}); // never answers
  await new Promise((r) => slow.listen(0, "127.0.0.1", r));
  try {
    const c = new Dipsac({ apiKey: "dps_test", baseUrl: `http://127.0.0.1:${slow.address().port}`, maxRetries: 0, timeout: 150 });
    await assert.rejects(c.dev.json({ content: "{}" }), dipsac.APITimeoutError);
  } finally {
    slow.closeAllConnections();
    slow.close();
  }
});

// ── jobs ────────────────────────────────────────────────────────────────────
test("mode async gives a Job that waits, then downloads", async () => {
  answers.push(
    j({ job_id: "j9", status: "queued", status_url: "/v1/jobs/j9" }, 202),
    j({ id: "j9", status: "running" }),
    j({ id: "j9", status: "succeeded", result_url: "/v1/jobs/j9/result" }),
    file(PDF, "application/pdf", "a-compressed.pdf"),
  );
  const job = await client().pdf.compress({ file: new Uint8Array(PDF), mode: "async" });
  assert.ok(job instanceof Job);
  assert.deepEqual([job.id, job.status], ["j9", "queued"]);
  const out = await job.wait({ pollInterval: 20 });
  assert.equal(out.filename, "a-compressed.pdf");
  assert.equal(job.status, "succeeded");
  assert.deepEqual(seen.map((r) => r.url), ["/v1/pdf/compress", "/v1/jobs/j9", "/v1/jobs/j9", "/v1/jobs/j9/result"]);
});

test("a failed job rejects with the API's reason; one that outlasts the wait is a timeout", async () => {
  answers.push(j({ job_id: "j9", status: "queued", status_url: "/v1/jobs/j9" }, 202), j({ id: "j9", status: "failed", error: "The file is not a valid video." }));
  const job = await client().video.mute({ file: { data: new Uint8Array([1]), filename: "a.mp4" }, mode: "async" });
  await assert.rejects(job.wait({ pollInterval: 10 }), (e) => e instanceof dipsac.JobFailedError && /not a valid video/.test(e.message) && e.job === job);
  answers.push(j({ job_id: "j8", status: "queued", status_url: "/v1/jobs/j8" }, 202), j({ id: "j8", status: "running" }));
  const slow = await client().pdf.compress({ file: new Uint8Array(PDF), mode: "async" });
  await assert.rejects(slow.wait({ timeout: 10, pollInterval: 50 }), (e) => e instanceof dipsac.JobTimeoutError && /still running/.test(e.message));
});

test("a speech job ends in done, and its audio is in the library", async () => {
  answers.push(
    j({ job_id: "s1", status: "queued", poll: "/ai/jobs/s1" }, 202),
    j({ job_id: "s1", status: "done", generation_id: 44, audio_url: "/ai/library/44/audio" }),
    file(Buffer.from("RIFFxxxxWAVE"), "audio/wav", "speech.wav"),
  );
  const job = await client().ai.speak({ text: "a long text", background: true });
  const audio = await job.wait({ pollInterval: 10 });
  assert.equal(audio.contentType, "audio/wav");
  assert.deepEqual(seen.map((r) => r.url), ["/ai/speak", "/ai/jobs/s1", "/ai/library/44/audio"]);
});

// ── the whole surface ───────────────────────────────────────────────────────
test("every operation in the schema has a method, and only those", async () => {
  const schema = JSON.parse(await readFile(new URL("../../openapi/dipsac.openapi.json", import.meta.url), "utf8"));
  const inSchema = new Set();
  for (const [path, item] of Object.entries(schema.paths))
    for (const m of Object.keys(item)) if (["get", "post", "put", "patch", "delete"].includes(m)) inSchema.add(`${m.toUpperCase()} ${path}`);
  const generated = new Set(dipsac.OPERATIONS.map(([m, p]) => `${m} ${p}`));
  assert.deepEqual([...generated].sort(), [...inSchema].sort());
  assert.equal(dipsac.OPERATIONS.length, 56);
  const c = client();
  for (const [, , resource, name] of dipsac.OPERATIONS) assert.equal(typeof c[resource][name], "function", `${resource}.${name}`);
});

test("the CommonJS build loads with require and is the same library", () => {
  const require = createRequire(import.meta.url);
  const cjs = require("../dist/cjs/index.js");
  assert.equal(typeof cjs.Dipsac, "function");
  assert.equal(cjs.VERSION, dipsac.VERSION);
  assert.equal(new cjs.Dipsac({ apiKey: "dps_x" }).baseUrl, "https://api.dipsac.com");
});
