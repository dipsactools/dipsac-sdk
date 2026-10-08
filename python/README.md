# DIPSAC Python library

The official Python library for the [DIPSAC API](https://dipsac.com/dashboard/reference):
PDF, image, audio, video and SEO tools, and the AI Voice Studio (text to speech,
transcription, subtitles).

```bash
pip install dipsac
```

Python 3.9 or newer. The only dependency is `httpx`.

## Quick start

Make a key at <https://dipsac.com/dashboard/keys>. Keys start with `dps_`.

```python
from dipsac import Dipsac

client = Dipsac(api_key="dps_...")        # or set the DIPSAC_API_KEY environment variable

# Files in, a file out
merged = client.pdf.merge(["invoice.pdf", "terms.pdf"])
merged.save("merged.pdf")

# Files in, facts out
info = client.image.info("photo.jpg")
print(info["width"], info["height"])

# No file at all
print(client.dev.json('{"b": 1, "a": 2}', sort_keys=True)["result"])
```

## What is in it

| | |
|---|---|
| `client.pdf` | merge, split, delete_pages, rotate, compress, convert, from_office, protect, unlock, watermark, metadata |
| `client.image` | convert, compress, resize, crop, remove_background, to_pdf, info |
| `client.audio` | convert, normalize, merge |
| `client.video` | convert, extract_audio, cut, resize, mute |
| `client.seo` | meta, ssl, redirects, whois, domain_age, canonical |
| `client.dev` | hash, hash_verify, json |
| `client.ai` | speak, transcribe, transcribe_video, subtitles, builtin_voices, voices, register_voice, library, ... |
| `client.jobs` | get, result |
| `client.glb` | limits, inspect, plan, image |

Every method is documented in its docstring, and typed. Which methods your key
may call depends on your plan; a call your plan does not include raises
`PermissionDeniedError`, which says which plan does.

## Giving it a file

Anywhere a method takes a file you can pass:

```python
client.pdf.metadata("report.pdf")                    # a path
client.pdf.metadata(Path("report.pdf"))              # a pathlib.Path
client.pdf.metadata(open("report.pdf", "rb"))        # an open binary file
client.pdf.metadata(pdf_bytes)                       # bytes
client.pdf.metadata(("report.pdf", pdf_bytes))       # a name and bytes
```

The API tells what a file is by the extension of its name. A path and an open
file bring their own name. Bare bytes have none, so the library reads their type
from how they begin (PDF, PNG, JPEG, GIF, WebP, WAV, MP3, MP4 and a few more);
for anything else, such as a Word file, pass the `(name, bytes)` form.

Uploads are read into memory before they are sent.

## What you get back

- **JSON** comes back as a `dict`.
- **A file** comes back as a `DipsacFile`:

  ```python
  out = client.image.convert("photo.png", "jpg")
  out.content        # the bytes
  out.content_type   # "image/jpeg"
  out.filename       # the name the API gave it, e.g. "photo.jpg"
  out.save("small.jpg")      # or out.save() to use that name, or out.save("some/folder")
  ```

- **A `Job`**, when you send the work to the background (next section).

## Long work: background jobs

Slow operations (video, big PDFs, background removal) take `mode="async"`. The
call returns at once with a `Job`; `wait()` polls until it is done and downloads
the result.

```python
job = client.video.convert("talk.mov", "mp4", mode="async")
clip = job.wait()                 # raises JobFailedError if the job fails
clip.save("talk.mp4")
```

`wait(timeout=600, poll_interval=2)` raises `JobTimeoutError` if the job is not
done in time. The job is not cancelled: keep `job.id` and pick it up later with
`client.job(job_id).wait()`. Results are kept for a limited time
(`job.raw["expires_at"]`).

## AI Voice Studio

```python
# Text to speech
audio = client.ai.speak("Namaste, aap kaise hain?", language="hi", fmt="mp3")
audio.save("hello.mp3")

# Long text: synthesise in the background
audio = client.ai.speak(long_text, language="en", background=True).wait()

# Speech to text
result = client.ai.transcribe("call.mp3", language="hi")
print(result["text"])

# Subtitles
client.ai.subtitles("episode.mp4", fmt="srt").save("episode.srt")

# Which voices exist
voices = client.ai.builtin_voices(language="hi")
```

Speech is metered per account. When an allowance is used up the call raises
`PaymentRequiredError`; `error.body` carries the numbers.

## Errors

Every error is a `dipsac.DipsacError`.

```python
import dipsac

try:
    client.audio.convert("voice.wav", "mp3")
except dipsac.PermissionDeniedError as e:
    print(e.message)             # "/v1/audio/convert requires the Pro plan or higher. ..."
    print(e.required_plan)       # "pro"
except dipsac.RateLimitError as e:
    print(e.retry_after)         # seconds
except dipsac.APIStatusError as e:
    print(e.status_code, e.code, e.message, e.request_id)
except dipsac.APIConnectionError:
    print("could not reach the API")
```

| Status | Exception | |
|---|---|---|
| 400 | `BadRequestError` | |
| 401 | `AuthenticationError` | the key is missing or wrong |
| 402 | `PaymentRequiredError` | an allowance is used up |
| 403 | `PermissionDeniedError` | the plan does not include this; `.required_plan` |
| 404 | `NotFoundError` | |
| 409 | `ConflictError` | e.g. a job that has not finished |
| 413 | `PayloadTooLargeError` | the file is over your plan's size limit |
| 415 | `UnsupportedMediaTypeError` | the wrong kind of file; `.accepted` |
| 422 | `UnprocessableEntityError` | a parameter is missing or invalid; `.fields` |
| 429 | `RateLimitError` | `.retry_after` |
| 5xx | `InternalServerError` | |
| | `APIConnectionError`, `APITimeoutError` | no answer |
| | `JobFailedError`, `JobTimeoutError` | background jobs |

Quote `e.request_id` when you write to support.

## Retries

The library sends a request again, up to `max_retries` times (default 2), only
where that cannot do the work twice:

- a `429` from your plan's per-second limit is waited out and retried;
- a `429` from your plan's monthly limit is raised at once (waiting would take a day);
- a connection that never opened is retried;
- a `GET` that got a 502, 503 or 504 is retried;
- a `POST` that failed on the server is **not** retried.

## Configuration

```python
client = Dipsac(
    api_key="dps_...",
    timeout=300,            # seconds; per call: client.pdf.compress(f, timeout=60)
    max_retries=2,
    base_url="https://api.dipsac.com",
)
```

`DIPSAC_API_KEY` and `DIPSAC_BASE_URL` are read from the environment when the
arguments are left out. Pass `http_client=httpx.Client(...)` to use a proxy or
your own transport.

## asyncio

```python
import asyncio
from dipsac import AsyncDipsac

async def main():
    async with AsyncDipsac() as client:
        merged = await client.pdf.merge(["a.pdf", "b.pdf"])
        job = await client.video.mute("clip.mp4", mode="async")
        muted = await job.wait()

asyncio.run(main())
```

## Links

- API reference: <https://dipsac.com/dashboard/reference>
- Speech API: <https://dipsac.com/dashboard/speech>
- Support: contact@dipsac.com
