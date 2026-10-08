# DIPSAC JavaScript and TypeScript library

The official library for the [DIPSAC API](https://dipsac.com/dashboard/reference):
PDF, image, audio, video and SEO tools, and the AI Voice Studio (text to speech,
transcription, subtitles).

```bash
npm install dipsac
```

Node.js 18 or newer. No dependencies. Types are included; it works from ES
modules and from `require`.

This library is for servers. Do not put an API key in code that runs in a
browser.

## Quick start

Make a key at <https://dipsac.com/dashboard/keys>. Keys start with `dps_`.

```js
import { Dipsac } from "dipsac";

const client = new Dipsac({ apiKey: "dps_..." });   // or set the DIPSAC_API_KEY environment variable

// Files in, a file out
const merged = await client.pdf.merge({ files: ["invoice.pdf", "terms.pdf"] });
await merged.save("merged.pdf");

// Files in, facts out
const info = await client.image.info({ file: "photo.jpg" });
console.log(info.width, info.height);

// No file at all
const out = await client.dev.json({ content: '{"b": 1, "a": 2}', sortKeys: true });
console.log(out.result);
```

## What is in it

| | |
|---|---|
| `client.pdf` | merge, split, deletePages, rotate, compress, convert, fromOffice, protect, unlock, watermark, metadata |
| `client.image` | convert, compress, resize, crop, removeBackground, toPdf, info |
| `client.audio` | convert, normalize, merge |
| `client.video` | convert, extractAudio, cut, resize, mute |
| `client.seo` | meta, ssl, redirects, whois, domainAge, canonical |
| `client.dev` | hash, hashVerify, json |
| `client.ai` | speak, transcribe, transcribeVideo, subtitles, builtinVoices, voices, registerVoice, library, ... |
| `client.jobs` | get, result |
| `client.glb` | limits, inspect, plan, image |

Every method takes one object of parameters, typed and documented. Which methods
your key may call depends on your plan; a call your plan does not include
rejects with `PermissionDeniedError`, which says which plan does.

## Giving it a file

Anywhere a method takes a file you can pass:

```js
await client.pdf.metadata({ file: "report.pdf" });                          // a path
await client.pdf.metadata({ file: await readFile("report.pdf") });          // a Buffer or Uint8Array
await client.pdf.metadata({ file: someBlobOrFile });                        // a Blob or File
await client.pdf.metadata({ file: { data: bytes, filename: "report.pdf" } });
```

The API tells what a file is by the extension of its name. A path and a `File`
bring their own name. Bare bytes have none, so the library reads their type from
how they begin (PDF, PNG, JPEG, GIF, WebP, WAV, MP3, MP4 and a few more); for
anything else, such as a Word file, pass `{ data, filename }`.

Uploads are held in memory before they are sent.

## What you get back

- **JSON** resolves to a plain object.
- **A file** resolves to a `DipsacFile`:

  ```js
  const out = await client.image.convert({ file: "photo.png", outputFormat: "jpg" });
  out.data          // Uint8Array
  out.contentType   // "image/jpeg"
  out.filename      // the name the API gave it, e.g. "photo.jpg"
  await out.save("small.jpg");   // or save() to use that name, or save("some/folder")
  out.text();       // the content as text (subtitles)
  ```

- **A `Job`**, when you send the work to the background (next section).

## Long work: background jobs

Slow operations (video, big PDFs, background removal) take `mode: "async"`. The
call resolves at once to a `Job`; `wait()` polls until it is done and downloads
the result.

```js
const job = await client.video.convert({ file: "talk.mov", outputFormat: "mp4", mode: "async" });
const clip = await job.wait();          // rejects with JobFailedError if the job fails
await clip.save("talk.mp4");
```

`wait({ timeout: 600000, pollInterval: 2000 })` rejects with `JobTimeoutError` if
the job is not done in time. The job is not cancelled: keep `job.id` and pick it
up later with `client.job(jobId).wait()`. Results are kept for a limited time
(`job.raw.expires_at`).

## AI Voice Studio

```js
// Text to speech
const audio = await client.ai.speak({ text: "Namaste, aap kaise hain?", language: "hi", fmt: "mp3" });
await audio.save("hello.mp3");

// Long text: synthesise in the background
const job = await client.ai.speak({ text: longText, language: "en", background: true });
const long = await job.wait();

// Speech to text
const result = await client.ai.transcribe({ file: "call.mp3", language: "hi" });
console.log(result.text);

// Subtitles
await (await client.ai.subtitles({ file: "episode.mp4", fmt: "srt" })).save("episode.srt");

// Which voices exist
const voices = await client.ai.builtinVoices({ language: "hi" });
```

Speech is metered per account. When an allowance is used up the call rejects
with `PaymentRequiredError`; `error.body` carries the numbers.

## Errors

Every error is a `DipsacError`.

```js
import { PermissionDeniedError, RateLimitError, APIStatusError, APIConnectionError } from "dipsac";

try {
  await client.audio.convert({ file: "voice.wav", outputFormat: "mp3" });
} catch (e) {
  if (e instanceof PermissionDeniedError) console.log(e.message, e.requiredPlan);   // "pro"
  else if (e instanceof RateLimitError) console.log(e.retryAfter);                  // seconds
  else if (e instanceof APIStatusError) console.log(e.status, e.code, e.message, e.requestId);
  else if (e instanceof APIConnectionError) console.log("could not reach the API");
  else throw e;
}
```

| Status | Error | |
|---|---|---|
| 400 | `BadRequestError` | |
| 401 | `AuthenticationError` | the key is missing or wrong |
| 402 | `PaymentRequiredError` | an allowance is used up |
| 403 | `PermissionDeniedError` | the plan does not include this; `.requiredPlan` |
| 404 | `NotFoundError` | |
| 409 | `ConflictError` | e.g. a job that has not finished |
| 413 | `PayloadTooLargeError` | the file is over your plan's size limit |
| 415 | `UnsupportedMediaTypeError` | the wrong kind of file; `.accepted` |
| 422 | `UnprocessableEntityError` | a parameter is missing or invalid; `.fields` |
| 429 | `RateLimitError` | `.retryAfter` |
| 5xx | `InternalServerError` | |
| | `APIConnectionError`, `APITimeoutError` | no answer |
| | `JobFailedError`, `JobTimeoutError` | background jobs |

Quote `e.requestId` when you write to support.

## Retries

The library sends a request again, up to `maxRetries` times (default 2), only
where that cannot do the work twice:

- a `429` from your plan's per-second limit is waited out and retried;
- a `429` from your plan's monthly limit is thrown at once (waiting would take a day);
- a `GET` that failed, or got a 502, 503 or 504, is retried;
- a `POST` that failed is **not** retried.

## Configuration

```js
const client = new Dipsac({
  apiKey: "dps_...",
  timeout: 300_000,       // milliseconds; per call: client.pdf.compress({ file }, { timeout: 60_000 })
  maxRetries: 2,
  baseUrl: "https://api.dipsac.com",
});
```

`DIPSAC_API_KEY` and `DIPSAC_BASE_URL` are read from the environment when the
options are left out. Pass `fetch` to use your own, for a proxy. Every method
takes a second argument, `{ timeout, signal }`, and `signal` aborts the call.

## CommonJS

```js
const { Dipsac } = require("dipsac");
```

## Links

- API reference: <https://dipsac.com/dashboard/reference>
- Speech API: <https://dipsac.com/dashboard/speech>
- Support: contact@dipsac.com
