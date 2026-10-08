// The library against a REAL server. Not part of `npm test`: run it by hand.
//
//   DIPSAC_BASE_URL=http://127.0.0.1:5051 DIPSAC_API_KEY=dps_... \
//   DIPSAC_FREE_KEY=dps_... node tests/live_smoke.mjs
//
// The unit tests prove what the library sends to a recording server. This
// proves a real one takes it: the multipart framing, the Content-Length, the
// file names, the job routes, and the error bodies as they really arrive.
// DIPSAC_API_KEY should be a key whose plan includes audio, video and GLB;
// DIPSAC_FREE_KEY (optional) is a Free key, used to meet the per-second limit.
//
// Speech is not here: it needs the GPU service, which a test server does not have.
import { readFile } from "node:fs/promises";
import { File } from "node:buffer"; // a global only from Node 20
import { fileURLToPath } from "node:url";

import * as dipsac from "../dist/esm/index.js";

const { Dipsac, DipsacFile, Job } = dipsac;
const fix = (name) => fileURLToPath(new URL(`../../fixtures/${name}`, import.meta.url));
let passed = 0;
let failed = 0;

function check(name, ok, detail) {
  if (ok) {
    passed++;
    console.log(`  PASS  ${name}`);
  } else {
    failed++;
    console.log(`  FAIL  ${name}  -> ${String(detail?.message ?? detail).slice(0, 300)}`);
  }
}
/** Run one call; a throw is a failed check, never the end of the run. */
async function attempt(name, fn) {
  try {
    return await fn();
  } catch (e) {
    check(name, false, `${e?.constructor?.name}: ${e?.message}`);
    return undefined;
  }
}
const isFile = (x, starts, type) =>
  x instanceof DipsacFile && Buffer.from(x.data.subarray(0, starts.length)).equals(Buffer.from(starts)) && x.contentType === type;

const client = new Dipsac();
console.log(`against ${client.baseUrl}`);

console.log("[1] PDF");
let out = await attempt("merge", () => client.pdf.merge({ files: [fix("doc.pdf"), fix("doc2.pdf")] }));
check("two paths merge into one PDF named by the API", isFile(out, "%PDF", "application/pdf") && out.filename === "merged.pdf", out);
const meta = await attempt("metadata", () => client.pdf.metadata({ file: out?.data ?? new Uint8Array() }));
check("the merged file has both documents' pages (3 + 2), read from bare bytes", meta?.pages === 5, JSON.stringify(meta));
out = await attempt("rotate", async () => client.pdf.rotate({ file: new File([await readFile(fix("doc.pdf"))], "doc.pdf"), degrees: 180 }));
check("a File is uploaded under its own name", isFile(out, "%PDF", "application/pdf") && out.filename === "doc-rotated.pdf", out);
out = await attempt("convert", () => client.pdf.convert({ file: fix("doc.pdf"), outputFormat: "docx" }));
check("PDF to Word answers with a .docx, which the schema calls JSON", out instanceof DipsacFile && out.data[0] === 0x50 && out.data[1] === 0x4b && String(out.filename).endsWith(".docx"), out);
out = await attempt("fromOffice", () => client.pdf.fromOffice({ file: fix("letter.docx") }));
check("Word to PDF", isFile(out, "%PDF", "application/pdf"), out);
out = await attempt("protect", () => client.pdf.protect({ file: fix("doc.pdf"), password: "s3cret", allowPrinting: false }));
check("a boolean reaches the server as it reads one", isFile(out, "%PDF", "application/pdf"), out);

console.log("[2] a background job");
let job = await attempt("compress async", () => client.pdf.compress({ file: fix("doc.pdf"), mode: "async" }));
check("mode 'async' answers with a Job that is queued", job instanceof Job && job.status === "queued" && job.id.length > 8, job);
if (job instanceof Job) {
  const done = await attempt("wait", () => job.wait({ timeout: 120_000, pollInterval: 1000 }));
  check("wait() ends in the file", isFile(done, "%PDF", "application/pdf") && job.status === "succeeded", done);
  const again = await attempt("job by id", () => client.job(job.id).wait({ timeout: 30_000, pollInterval: 1000 }));
  check("the same job can be fetched again by its id", again instanceof DipsacFile && Buffer.from(again.data).equals(Buffer.from(done?.data ?? [])), again);
  const status = await attempt("jobs.get", () => client.jobs.get(job.id));
  check("jobs.get is the API's own status body", status?.status === "succeeded" && "expires_at" in (status ?? {}), JSON.stringify(status));
}

console.log("[3] images, audio, video");
const info = await attempt("image.info", () => client.image.info({ file: fix("photo.png") }));
check("image facts as an object", info?.width === 320 && info?.height === 200, JSON.stringify(info));
out = await attempt("image.convert", () => client.image.convert({ file: fix("photo.png"), outputFormat: "jpg", quality: 80 }));
check("PNG to JPEG", out instanceof DipsacFile && out.contentType === "image/jpeg" && out.data[0] === 0xff && out.data[1] === 0xd8, out);
out = await attempt("image.toPdf", () => client.image.toPdf({ files: [fix("photo.png"), fix("photo.png")] }));
check("images into one PDF", isFile(out, "%PDF", "application/pdf"), out);
out = await attempt("audio.convert", () => client.audio.convert({ file: fix("tone.wav"), outputFormat: "mp3" }));
check("WAV to MP3", out instanceof DipsacFile && out.contentType === "audio/mpeg" && out.size > 500, out);
job = await attempt("video.mute async", () => client.video.mute({ file: fix("clip.mp4"), mode: "async" }));
out = job instanceof Job ? await attempt("video wait", () => job.wait({ timeout: 180_000, pollInterval: 1000 })) : undefined;
check("a video job, waited for", out instanceof DipsacFile && out.contentType === "video/mp4", out);

console.log("[4] JSON in, JSON out");
const tags = await attempt("seo.meta", () => client.seo.meta({ title: "A title", description: "A description", url: "https://example.com" }));
check("meta tags", String(tags?.html).includes("<title>A title</title>"), JSON.stringify(tags).slice(0, 120));
const hashed = await attempt("dev.hash", () => client.dev.hash({ password: "hunter2", rounds: 4 }));
const verdict = await attempt("dev.hashVerify", () => client.dev.hashVerify({ password: "hunter2", hash: hashed?.hash ?? "" }));
check("a hash made by one call is verified by the other", Object.values(verdict ?? {}).includes(true), JSON.stringify(verdict));
const limits = await attempt("glb.limits", () => client.glb.limits());
check("a GET with no parameters", limits && "max_ops" in limits, JSON.stringify(limits).slice(0, 80));

console.log("[5] refusals, as they really arrive");
await new Dipsac({ apiKey: "dps_not_a_real_key", maxRetries: 0 }).dev.json({ content: "{}" }).then(
  () => check("a wrong key is refused", false, "no error"),
  (e) => check("a wrong key is AuthenticationError with the API's code and a request id", e instanceof dipsac.AuthenticationError && e.status === 401 && e.code === "unauthorized" && !!e.requestId, e),
);
await client.pdf.metadata({ file: { data: new Uint8Array([104, 105]), filename: "notes.txt" } }).then(
  () => check("the wrong kind of file is refused", false, "no error"),
  (e) => check("the wrong kind of file names what is accepted", e instanceof dipsac.UnsupportedMediaTypeError && e.accepted?.[0] === ".pdf", e),
);
await client.jobs.get("0".repeat(32)).then(
  () => check("an unknown job is refused", false, "no error"),
  (e) => check("an unknown job is NotFoundError", e instanceof dipsac.NotFoundError && e.code === "not_found", e),
);

if (process.env.DIPSAC_FREE_KEY) {
  console.log("[6] the per-second limit, met for real with a Free key");
  const free = new Dipsac({ apiKey: process.env.DIPSAC_FREE_KEY, maxRetries: 4 });
  const blunt = new Dipsac({ apiKey: process.env.DIPSAC_FREE_KEY, maxRetries: 0 });
  await new Promise((r) => setTimeout(r, 1200));
  let refused = 0;
  let last;
  for (let i = 0; i < 6; i++) {
    await blunt.dev.json({ content: "{}" }).catch((e) => {
      if (e instanceof dipsac.RateLimitError) {
        refused++;
        last = e;
      }
    });
  }
  check("FIXTURE: with retries off, a burst of six IS refused -- otherwise the next check proves nothing", refused >= 1 && last?.retryAfter === 1 && last?.code === "rate_limited", refused);
  await new Promise((r) => setTimeout(r, 1200));
  const started = Date.now();
  const answers = await attempt("burst", async () => {
    const all = [];
    for (let i = 0; i < 6; i++) all.push(await free.dev.json({ content: "{}" }));
    return all;
  });
  check("with retries on, the same burst all succeeds, and it took real waiting", answers?.length === 6 && Date.now() - started > 900, `${answers?.length} in ${Date.now() - started} ms`);
  await free.audio.convert({ file: fix("tone.wav"), outputFormat: "mp3" }).then(
    () => check("a Free key is refused audio", false, "no error"),
    (e) => check("a plan refusal says which plan is needed", e instanceof dipsac.PermissionDeniedError && e.currentPlan === "free" && e.requiredPlan === "pro", e),
  );
}

console.log(`\nPASSED ${passed}  FAILED ${failed}`);
process.exit(failed ? 1 : 0);
