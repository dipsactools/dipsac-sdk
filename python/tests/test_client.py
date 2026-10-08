"""The transport, against a fake server that records what it was sent.

No network. Each test names the one thing it would catch going wrong.
"""
from __future__ import annotations

import io
import json
from pathlib import Path

import httpx
import pytest

import dipsac
from dipsac import AsyncDipsac, Dipsac, DipsacFile, Job

PDF = b"%PDF-1.7\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF\n"


class Fake:
    """A server made of a list of answers, handed out in order."""

    def __init__(self, *answers):
        self.answers = list(answers)
        self.requests = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        request.read()
        self.requests.append(request)
        if not self.answers:
            raise AssertionError(f"an unexpected request: {request.method} {request.url}")
        answer = self.answers.pop(0)
        if isinstance(answer, Exception):
            raise answer
        return answer


def client_for(fake, **kw) -> Dipsac:
    kw.setdefault("api_key", "dps_test")
    return Dipsac(http_client=httpx.Client(transport=httpx.MockTransport(fake)), **kw)


def j(status=200, body=None, **headers):
    return httpx.Response(status, json=body if body is not None else {}, headers=headers)


def binary(content=PDF, ctype="application/pdf", name="out.pdf", **headers):
    return httpx.Response(200, content=content, headers={
        "content-type": ctype, "content-disposition": f'attachment; filename="{name}"', **headers})


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    """Retries and polls wait; the tests do not."""
    slept = []
    monkeypatch.setattr("time.sleep", lambda s: slept.append(s))
    return slept


# ── who we say we are ────────────────────────────────────────────────────────
def test_the_key_goes_in_x_api_key_and_the_library_names_itself():
    fake = Fake(j(body={"ok": True}))
    client_for(fake).dev.json("{}")
    sent = fake.requests[0]
    assert sent.headers["x-api-key"] == "dps_test"
    assert sent.headers["user-agent"] == f"dipsac-python/{dipsac.__version__}"
    assert str(sent.url) == "https://api.dipsac.com/v1/dev/json"


def test_no_key_anywhere_is_refused_before_any_request(monkeypatch):
    monkeypatch.delenv("DIPSAC_API_KEY", raising=False)
    with pytest.raises(dipsac.DipsacError, match="No API key"):
        Dipsac()


def test_the_key_and_the_address_can_come_from_the_environment(monkeypatch):
    monkeypatch.setenv("DIPSAC_API_KEY", "dps_env")
    monkeypatch.setenv("DIPSAC_BASE_URL", "http://127.0.0.1:5051/")
    fake = Fake(j())
    c = Dipsac(http_client=httpx.Client(transport=httpx.MockTransport(fake)))
    c.dev.json("{}")
    assert fake.requests[0].headers["x-api-key"] == "dps_env"
    assert str(fake.requests[0].url) == "http://127.0.0.1:5051/v1/dev/json"


# ── what is sent ─────────────────────────────────────────────────────────────
def test_json_body_leaves_out_what_the_caller_left_out():
    fake = Fake(j())
    client_for(fake).dev.json('{"a":1}', sort_keys=True)
    assert json.loads(fake.requests[0].content) == {"content": '{"a":1}', "sort_keys": True}


def test_query_parameters_for_a_get():
    fake = Fake(j())
    client_for(fake).seo.ssl("example.com")
    assert fake.requests[0].method == "GET"
    assert fake.requests[0].url.params["url"] == "example.com"


def test_an_upload_is_multipart_with_a_length_a_name_and_string_fields(tmp_path):
    path = tmp_path / "report.pdf"
    path.write_bytes(PDF)
    fake = Fake(binary())
    client_for(fake).pdf.compress(path, preset="screen", remove_metadata=False)
    sent = fake.requests[0]
    assert sent.headers["content-type"].startswith("multipart/form-data; boundary=")
    # The API answers 411 to an upload with no length, so chunked would be a refusal.
    assert int(sent.headers["content-length"]) == len(sent.content)
    assert "transfer-encoding" not in sent.headers
    body = sent.content
    assert b'name="file"; filename="report.pdf"' in body and PDF in body
    assert b'name="preset"\r\n\r\nscreen' in body
    assert b'name="remove_metadata"\r\n\r\nfalse' in body          # not Python's "False"
    assert b'name="mode"' not in body                              # left out, so the server's default applies


def test_several_files_go_under_one_repeated_name_in_order():
    fake = Fake(binary())
    client_for(fake).pdf.merge([("first.pdf", PDF), ("second.pdf", PDF + b"2")])
    body = fake.requests[0].content
    a, b = body.find(b'filename="first.pdf"'), body.find(b'filename="second.pdf"')
    assert 0 < a < b
    assert body.count(b'name="files"') == 2


def test_a_name_and_bytes_tuple_is_one_file_not_two():
    fake = Fake(j())
    client_for(fake).pdf.metadata(("contract.pdf", PDF))
    body = fake.requests[0].content
    assert body.count(b'name="file"') == 1 and b'filename="contract.pdf"' in body


def test_bare_bytes_are_named_by_what_they_are():
    fake = Fake(j(), j())
    c = client_for(fake)
    c.pdf.metadata(PDF)
    c.image.info(b"\x89PNG\r\n\x1a\n" + b"\x00" * 20)
    assert b'filename="file.pdf"' in fake.requests[0].content
    assert b'filename="file.png"' in fake.requests[1].content


def test_an_open_file_keeps_its_own_name(tmp_path):
    path = tmp_path / "scan.pdf"
    path.write_bytes(PDF)
    fake = Fake(j())
    with open(path, "rb") as fh:
        client_for(fake).pdf.metadata(fh)
    assert b'filename="scan.pdf"' in fake.requests[0].content


def test_a_file_opened_as_text_is_refused_with_a_reason():
    with pytest.raises(TypeError, match="binary mode"):
        client_for(Fake()).pdf.metadata(io.StringIO("not bytes"))


def test_speech_is_a_form_and_background_travels_as_async():
    fake = Fake(binary(b"RIFFxxxxWAVE", "audio/wav", "speech.wav"))
    client_for(fake).ai.speak("Namaste", language="hi", speed=1.1)
    sent = fake.requests[0]
    assert sent.headers["content-type"] == "application/x-www-form-urlencoded"
    assert dict(httpx.QueryParams(sent.content.decode())) == {"text": "Namaste", "language": "hi", "speed": "1.1"}
    fake2 = Fake(j(202, {"job_id": "j1", "status": "queued", "poll": "/ai/jobs/j1"}))
    client_for(fake2).ai.speak("long text", background=True)
    assert dict(httpx.QueryParams(fake2.requests[0].content.decode()))["async"] == "true"


def test_a_path_parameter_is_escaped():
    fake = Fake(j())
    client_for(fake).jobs.get("a/b c")
    assert fake.requests[0].url.raw_path == b"/v1/jobs/a%2Fb%20c"


# ── what comes back ──────────────────────────────────────────────────────────
def test_json_comes_back_as_a_dict():
    assert client_for(Fake(j(body={"width": 320}))).image.info(PDF) == {"width": 320}


def test_a_file_comes_back_with_its_name_type_and_headers(tmp_path):
    fake = Fake(binary(name="merged.pdf", **{"x-original-size": "856"}))
    out = client_for(fake).pdf.merge([PDF, PDF])
    assert isinstance(out, DipsacFile)
    assert (out.content, out.content_type, out.filename, out.size) == (PDF, "application/pdf", "merged.pdf", len(PDF))
    assert out.headers["x-original-size"] == "856"
    assert out.save(tmp_path).read_bytes() == PDF and (tmp_path / "merged.pdf").exists()
    assert out.save(tmp_path / "mine.pdf") == tmp_path / "mine.pdf"


def test_a_name_that_is_not_ascii_is_read_from_the_utf8_form():
    r = httpx.Response(200, content=PDF, headers={
        "content-type": "application/pdf",
        "content-disposition": "attachment; filename=\"document_signed.pdf\"; "
                               "filename*=UTF-8''%E0%A4%85%E0%A4%A8%E0%A5%81%E0%A4%AC%E0%A4%82%E0%A4%A7_signed.pdf"})
    assert client_for(Fake(r)).pdf.unlock(PDF).filename == "अनुबंध_signed.pdf"


def test_a_name_cannot_point_outside_the_folder_it_is_saved_in(tmp_path):
    r = httpx.Response(200, content=PDF, headers={
        "content-type": "application/pdf", "content-disposition": 'attachment; filename="../../evil.pdf"'})
    out = client_for(Fake(r)).pdf.unlock(PDF)
    assert out.filename == "evil.pdf"
    assert out.save(tmp_path).parent == tmp_path


def test_subtitles_come_back_as_text():
    r = httpx.Response(200, content="1\n00:00:00,000 --> 00:00:01,000\nनमस्ते\n".encode(),
                       headers={"content-type": "text/plain; charset=utf-8"})
    assert "नमस्ते" in client_for(Fake(r)).ai.subtitles(("a.mp3", b"ID3x")).text


# ── errors ───────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("status,cls", [
    (400, dipsac.BadRequestError), (401, dipsac.AuthenticationError), (402, dipsac.PaymentRequiredError),
    (403, dipsac.PermissionDeniedError), (404, dipsac.NotFoundError), (409, dipsac.ConflictError),
    (413, dipsac.PayloadTooLargeError), (415, dipsac.UnsupportedMediaTypeError),
    (422, dipsac.UnprocessableEntityError), (500, dipsac.InternalServerError), (418, dipsac.APIStatusError),
])
def test_each_status_is_its_own_exception_with_the_apis_words(status, cls):
    body = {"error": "some_code", "message": "A sentence.", "request_id": "rid1", "detail": "A sentence."}
    with pytest.raises(cls) as caught:
        client_for(Fake(j(status, body))).dev.json("{}")
    e = caught.value
    assert type(e) is cls
    assert (e.status_code, e.code, e.message, e.request_id, e.body) == (status, "some_code", "A sentence.", "rid1", body)
    assert "A sentence." in str(e) and "rid1" in str(e)


def test_the_extra_fields_of_three_refusals_are_readable():
    c = lambda body, status: client_for(Fake(j(status, body)))
    with pytest.raises(dipsac.PermissionDeniedError) as e:
        c({"error": "upgrade_required", "message": "m", "current_plan": "free", "required_plan": "pro"}, 403).audio.merge([PDF])
    assert (e.value.current_plan, e.value.required_plan) == ("free", "pro")
    with pytest.raises(dipsac.UnsupportedMediaTypeError) as e:
        c({"error": "unsupported_media_type", "message": "m", "accepted": [".pdf"]}, 415).pdf.metadata(("a.txt", b"x"))
    assert e.value.accepted == [".pdf"]
    with pytest.raises(dipsac.UnprocessableEntityError) as e:
        c({"error": "invalid_request", "message": "m", "fields": [{"field": "content"}]}, 422).dev.json("")
    assert e.value.fields == [{"field": "content"}]


def test_an_error_that_is_not_json_still_says_something():
    r = httpx.Response(502, content=b"<html>Bad Gateway</html>", headers={"content-type": "text/html", "x-request-id": "edge1"})
    with pytest.raises(dipsac.InternalServerError) as e:
        client_for(Fake(r), max_retries=0).dev.json("{}")
    assert "Bad Gateway" in e.value.message and e.value.request_id == "edge1"


# ── retries ──────────────────────────────────────────────────────────────────
def test_the_per_second_limit_is_waited_out_and_the_request_sent_again(no_sleep):
    limited = j(429, {"error": "rate_limited", "message": "2 requests/second"}, **{"retry-after": "1"})
    fake = Fake(limited, j(body={"valid": True}))
    assert client_for(fake).dev.json("{}") == {"valid": True}
    assert len(fake.requests) == 2 and no_sleep == [1.0]


def test_the_monthly_limit_is_raised_at_once_and_not_slept_through(no_sleep):
    used_up = j(429, {"error": "rate_limited", "message": "Monthly request limit of 500 reached"}, **{"retry-after": "86400"})
    fake = Fake(used_up)
    with pytest.raises(dipsac.RateLimitError) as e:
        client_for(fake).dev.json("{}")
    assert e.value.retry_after == 86400.0 and len(fake.requests) == 1 and no_sleep == []


def test_a_limit_that_never_lifts_gives_up_after_max_retries():
    limited = lambda: j(429, {"error": "rate_limited", "message": "m"}, **{"retry-after": "1"})
    fake = Fake(limited(), limited(), limited())
    with pytest.raises(dipsac.RateLimitError):
        client_for(fake, max_retries=2).dev.json("{}")
    assert len(fake.requests) == 3


def test_a_post_that_failed_on_the_server_is_not_sent_twice():
    fake = Fake(j(503, {"error": "service_unavailable", "message": "m"}))
    with pytest.raises(dipsac.InternalServerError):
        client_for(fake).ai.speak("paid for per call")
    assert len(fake.requests) == 1


def test_a_get_that_failed_on_the_server_is_tried_again():
    fake = Fake(j(503, {"error": "x", "message": "m"}), j(body={"status": "running"}))
    assert client_for(fake).jobs.get("j1") == {"status": "running"}
    assert len(fake.requests) == 2


def test_a_connection_that_never_opened_is_tried_again_even_for_a_post():
    fake = Fake(httpx.ConnectError("refused"), j(body={"ok": 1}))
    assert client_for(fake).dev.json("{}") == {"ok": 1}


def test_a_post_whose_connection_broke_midway_is_not_sent_twice():
    fake = Fake(httpx.ReadError("reset"))
    with pytest.raises(dipsac.APIConnectionError):
        client_for(fake).dev.json("{}")
    assert len(fake.requests) == 1


def test_a_timeout_is_its_own_error():
    with pytest.raises(dipsac.APITimeoutError):
        client_for(Fake(httpx.ReadTimeout("slow")), max_retries=0).dev.json("{}")


# ── jobs ─────────────────────────────────────────────────────────────────────
def test_mode_async_gives_a_job_that_waits_then_downloads(no_sleep):
    accepted = j(202, {"job_id": "j9", "status": "queued", "status_url": "/v1/jobs/j9"})
    fake = Fake(accepted,
                j(body={"id": "j9", "status": "running"}),
                j(body={"id": "j9", "status": "succeeded", "result_url": "/v1/jobs/j9/result"}),
                binary(name="a-compressed.pdf"))
    job = client_for(fake).pdf.compress(PDF, mode="async")
    assert isinstance(job, Job) and (job.id, job.status) == ("j9", "queued")
    out = job.wait(poll_interval=2.0)
    assert out.filename == "a-compressed.pdf" and job.status == "succeeded"
    assert [r.url.path for r in fake.requests] == ["/v1/pdf/compress", "/v1/jobs/j9", "/v1/jobs/j9", "/v1/jobs/j9/result"]
    assert no_sleep == [2.0]


def test_a_failed_job_raises_with_the_apis_reason():
    fake = Fake(j(202, {"job_id": "j9", "status": "queued", "status_url": "/v1/jobs/j9"}),
                j(body={"id": "j9", "status": "failed", "error": "The file is not a valid video."}))
    job = client_for(fake).video.mute(("a.mp4", b"x"), mode="async")
    with pytest.raises(dipsac.JobFailedError, match="not a valid video") as e:
        job.wait()
    assert e.value.job is job


def test_a_job_that_outlasts_the_wait_is_a_timeout_and_is_not_lost():
    fake = Fake(j(202, {"job_id": "j9", "status": "queued", "status_url": "/v1/jobs/j9"}),
                j(body={"id": "j9", "status": "running"}))
    job = client_for(fake).pdf.compress(PDF, mode="async")
    with pytest.raises(dipsac.JobTimeoutError, match="still running") as e:
        job.wait(timeout=1.0, poll_interval=2.0)
    assert e.value.job.id == "j9"


def test_a_speech_job_ends_in_done_and_its_audio_is_in_the_library():
    fake = Fake(j(202, {"job_id": "s1", "status": "queued", "poll": "/ai/jobs/s1"}),
                j(body={"job_id": "s1", "status": "done", "generation_id": 44, "audio_url": "/ai/library/44/audio"}),
                binary(b"RIFFxxxxWAVE", "audio/wav", "speech.wav"))
    audio = client_for(fake).ai.speak("a long text", background=True).wait()
    assert audio.content_type == "audio/wav"
    assert [r.url.path for r in fake.requests] == ["/ai/speak", "/ai/jobs/s1", "/ai/library/44/audio"]


def test_a_job_can_be_picked_up_again_by_its_id():
    fake = Fake(j(body={"id": "j9", "status": "succeeded", "result_url": "/v1/jobs/j9/result"}), binary())
    assert client_for(fake).job("j9").wait().content == PDF


# ── the whole surface ────────────────────────────────────────────────────────
def test_every_operation_in_the_schema_has_a_method_and_only_those():
    from dipsac._resources import OPERATIONS
    schema = json.loads((Path(__file__).resolve().parents[2] / "openapi" / "dipsac.openapi.json").read_text("utf-8"))
    in_schema = {(m.upper(), p) for p, item in schema["paths"].items() for m in item if m in ("get", "post", "put", "patch", "delete")}
    generated = {(m, p) for m, p, _r, _n in OPERATIONS}
    assert generated == in_schema and len(OPERATIONS) == len(in_schema) == 56
    c = client_for(Fake())
    for _m, _p, resource, name in OPERATIONS:
        assert callable(getattr(getattr(c, resource), name)), f"{resource}.{name}"


def test_what_only_a_browser_can_send_is_not_offered():
    import inspect
    c = client_for(Fake())
    for method in (c.ai.speak, c.ai.transcribe, c.ai.subtitles, c.ai.status):
        params = inspect.signature(method).parameters
        assert "turnstile_token" not in params and "access_token" not in params and "async" not in params
    assert "background" in inspect.signature(c.ai.speak).parameters


# ── asyncio ──────────────────────────────────────────────────────────────────
async def test_the_async_client_sends_the_same_request_and_waits_on_a_job(monkeypatch):
    slept = []

    async def nap(s):
        slept.append(s)
    monkeypatch.setattr("asyncio.sleep", nap)
    fake = Fake(j(202, {"job_id": "j9", "status": "queued", "status_url": "/v1/jobs/j9"}),
                j(body={"id": "j9", "status": "succeeded", "result_url": "/v1/jobs/j9/result"}),
                binary(name="out.pdf"))
    async with AsyncDipsac(api_key="dps_test", http_client=httpx.AsyncClient(transport=httpx.MockTransport(fake))) as c:
        job = await c.pdf.compress(("a.pdf", PDF), mode="async")
        assert isinstance(job, dipsac.AsyncJob)
        out = await job.wait()
    assert out.filename == "out.pdf"
    assert fake.requests[0].headers["x-api-key"] == "dps_test"
    assert b'name="mode"\r\n\r\nasync' in fake.requests[0].content


async def test_the_async_client_retries_the_per_second_limit(monkeypatch):
    async def nap(_s):
        return None
    monkeypatch.setattr("asyncio.sleep", nap)
    fake = Fake(j(429, {"error": "rate_limited", "message": "m"}, **{"retry-after": "1"}), j(body={"ok": 1}))
    async with AsyncDipsac(api_key="dps_test", http_client=httpx.AsyncClient(transport=httpx.MockTransport(fake))) as c:
        assert await c.dev.json("{}") == {"ok": 1}
