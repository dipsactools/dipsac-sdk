"""The transport: auth, uploads, errors, retries. One method per endpoint lives in
_resources.py, which is generated; everything here is what those methods share.

WHAT IS RETRIED, AND WHAT IS DELIBERATELY NOT.

  * A 429 whose Retry-After is short (the per-second limit; the Free plan allows
    two requests a second) is waited out and sent again. The API refused it
    before doing any work, so sending it again cannot do the work twice.
  * A 429 that asks for a long wait is the plan's MONTHLY limit. Waiting a day
    inside a function call helps nobody, so it is raised at once.
  * A connection that could not be opened is tried again: nothing was sent.
  * A GET that got 502, 503 or 504, or lost its connection, is tried again.
  * A POST that got a 5xx or lost its connection part-way is NOT. The server may
    have done the work, and some of it (speech) is paid for per call.
"""
from __future__ import annotations

import asyncio
import os
import random
import time
from typing import Any, Dict, List, Mapping, Optional, Tuple

import httpx

from ._errors import APIConnectionError, APITimeoutError, DipsacError, error_for
from ._files import to_part
from ._models import AsyncJob, DipsacFile, Job, filename_from
from ._resources import RESOURCES
from ._version import __version__

DEFAULT_BASE_URL = "https://api.dipsac.com"
DEFAULT_TIMEOUT = 300.0
DEFAULT_MAX_RETRIES = 2
# The longest Retry-After worth sleeping through. The per-second limit asks for
# 1; the monthly limit asks for 86400.
MAX_RETRY_AFTER = 30.0


def _scalar(value: Any) -> str:
    """A form or query value as the API reads it."""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _clean(values: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    """Without the entries the caller left out, so the server's defaults apply."""
    return {k: v for k, v in (values or {}).items() if v is not None}


class _Core:
    """What the sync and the async client have in common: everything but the wire."""

    def __init__(self, api_key: Optional[str], base_url: Optional[str], timeout: float,
                 max_retries: int, default_headers: Optional[Mapping[str, str]]) -> None:
        api_key = api_key or os.environ.get("DIPSAC_API_KEY")
        if not api_key:
            raise DipsacError(
                "No API key. Pass api_key=\"dps_...\" or set the DIPSAC_API_KEY environment "
                "variable. Keys are made at https://dipsac.com/dashboard/keys")
        self.api_key = api_key
        self.base_url = (base_url or os.environ.get("DIPSAC_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout
        self.max_retries = max(0, int(max_retries))
        self._headers = {"X-API-Key": api_key, "User-Agent": f"dipsac-python/{__version__}",
                         "Accept": "*/*", **dict(default_headers or {})}

    def _build(self, method: str, path: str, *, query: Optional[Mapping[str, Any]],
               json: Optional[Mapping[str, Any]], form: Optional[Mapping[str, Any]],
               files: Optional[Mapping[str, Any]], timeout: Optional[float]) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {
            "method": method,
            "url": path if path.startswith(("http://", "https://")) else self.base_url + path,
            "timeout": self.timeout if timeout is None else timeout,
        }
        q = {k: _scalar(v) for k, v in _clean(query).items()}
        if q:
            kwargs["params"] = q
        if json is not None:
            kwargs["json"] = _clean(json)
        fields = {k: _scalar(v) for k, v in _clean(form).items()}
        parts: List[Tuple[str, Tuple[str, bytes, str]]] = []
        for name, value in _clean(files).items():
            many = value if isinstance(value, (list, tuple)) and not _is_file_tuple(value) else [value]
            for one in many:
                parts.append((name, to_part(one, name)))
        if parts:
            kwargs["files"] = parts
        if fields:
            kwargs["data"] = fields
        return kwargs

    def _parse(self, response: httpx.Response) -> Tuple[str, Any]:
        """("json" | "file" | "job" | "none", value), or raise for an error status."""
        ctype = (response.headers.get("content-type") or "").split(";")[0].strip().lower()
        is_json = ctype == "application/json" or ctype.endswith("+json")
        if response.status_code >= 400:
            body: Any
            try:
                body = response.json() if is_json else response.text
            except ValueError:
                body = response.text
            raise error_for(response.status_code, body, response.headers)
        if is_json:
            data = response.json()
            if response.status_code == 202 and isinstance(data, dict) and data.get("job_id"):
                return "job", data
            return "json", data
        if not response.content:
            return "none", None
        return "file", DipsacFile(response.content, content_type=ctype or "application/octet-stream",
                                  filename=filename_from(response.headers), headers=response.headers)

    def _retry_in(self, attempt: int, method: str, *, response: Optional[httpx.Response] = None,
                  exc: Optional[BaseException] = None) -> Optional[float]:
        """Seconds to wait before another try, or None to give up. See the header."""
        if attempt >= self.max_retries:
            return None
        backoff = min(8.0, 0.5 * (2 ** attempt)) * (0.75 + random.random() / 2)
        if exc is not None:
            never_sent = isinstance(exc, (httpx.ConnectError, httpx.ConnectTimeout))
            return backoff if never_sent or method == "GET" else None
        assert response is not None
        if response.status_code == 429:
            try:
                asked = float(response.headers.get("retry-after", "1"))
            except ValueError:
                asked = 1.0
            return max(asked, 0.2) if asked <= MAX_RETRY_AFTER else None
        if response.status_code in (502, 503, 504) and method == "GET":
            return backoff
        return None


def _is_file_tuple(value: Any) -> bool:
    """("name.pdf", content[, type]) is ONE file, not a list of two or three."""
    return (isinstance(value, tuple) and len(value) in (2, 3) and isinstance(value[0], str)
            and not isinstance(value[1], (str, os.PathLike)) and (len(value) == 2 or isinstance(value[2], str)))


def _wrap(exc: httpx.HTTPError) -> APIConnectionError:
    if isinstance(exc, httpx.TimeoutException):
        return APITimeoutError(f"No answer from the API within the timeout ({type(exc).__name__}).")
    return APIConnectionError(f"Could not reach the API ({type(exc).__name__}: {exc}).")


class Dipsac(_Core):
    """The DIPSAC API.

        from dipsac import Dipsac

        client = Dipsac(api_key="dps_...")       # or set DIPSAC_API_KEY
        client.pdf.merge(["a.pdf", "b.pdf"]).save("merged.pdf")

    Args:
        api_key: your key; read from DIPSAC_API_KEY when left out.
        base_url: the API's address; https://api.dipsac.com unless set.
        timeout: seconds to wait for an answer (default 300; conversions take time).
        max_retries: how many times a refused or unsent request is tried again.
        default_headers: extra headers for every request.
        http_client: your own httpx.Client, e.g. for a proxy.
    """

    def __init__(self, api_key: Optional[str] = None, *, base_url: Optional[str] = None,
                 timeout: float = DEFAULT_TIMEOUT, max_retries: int = DEFAULT_MAX_RETRIES,
                 default_headers: Optional[Mapping[str, str]] = None,
                 http_client: Optional[httpx.Client] = None) -> None:
        super().__init__(api_key, base_url, timeout, max_retries, default_headers)
        self._http = http_client or httpx.Client(follow_redirects=False)
        self._owns_http = http_client is None
        for name, (sync_cls, _async_cls) in RESOURCES.items():
            setattr(self, name, sync_cls(self))

    def job(self, job_id: str) -> Job:
        """A handle on a /v1 job you already have the id of. Makes no request."""
        return Job(self, {"job_id": job_id, "status_url": f"/v1/jobs/{job_id}"})

    def _request(self, method: str, path: str, *, query: Optional[Mapping[str, Any]] = None,
                 json: Optional[Mapping[str, Any]] = None, form: Optional[Mapping[str, Any]] = None,
                 files: Optional[Mapping[str, Any]] = None, multipart: bool = False,
                 timeout: Optional[float] = None) -> Any:
        kwargs = self._build(method, path, query=query, json=json, form=form, files=files, timeout=timeout)
        attempt = 0
        while True:
            try:
                response = self._http.request(headers=self._headers, **kwargs)
            except httpx.HTTPError as exc:
                wait = self._retry_in(attempt, method, exc=exc)
                if wait is None:
                    raise _wrap(exc) from exc
            else:
                wait = self._retry_in(attempt, method, response=response)
                if wait is None:
                    kind, value = self._parse(response)
                    return Job(self, value) if kind == "job" else value
            attempt += 1
            time.sleep(wait)

    def close(self) -> None:
        if self._owns_http:
            self._http.close()

    def __enter__(self) -> "Dipsac":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()


class AsyncDipsac(_Core):
    """The DIPSAC API, for asyncio. Same methods as Dipsac, awaited.

        async with AsyncDipsac() as client:
            merged = await client.pdf.merge(["a.pdf", "b.pdf"])
    """

    def __init__(self, api_key: Optional[str] = None, *, base_url: Optional[str] = None,
                 timeout: float = DEFAULT_TIMEOUT, max_retries: int = DEFAULT_MAX_RETRIES,
                 default_headers: Optional[Mapping[str, str]] = None,
                 http_client: Optional[httpx.AsyncClient] = None) -> None:
        super().__init__(api_key, base_url, timeout, max_retries, default_headers)
        self._http = http_client or httpx.AsyncClient(follow_redirects=False)
        self._owns_http = http_client is None
        for name, (_sync_cls, async_cls) in RESOURCES.items():
            setattr(self, name, async_cls(self))

    def job(self, job_id: str) -> AsyncJob:
        """A handle on a /v1 job you already have the id of. Makes no request."""
        return AsyncJob(self, {"job_id": job_id, "status_url": f"/v1/jobs/{job_id}"})

    async def _request(self, method: str, path: str, *, query: Optional[Mapping[str, Any]] = None,
                       json: Optional[Mapping[str, Any]] = None, form: Optional[Mapping[str, Any]] = None,
                       files: Optional[Mapping[str, Any]] = None, multipart: bool = False,
                       timeout: Optional[float] = None) -> Any:
        # Reading the files is blocking work; a large upload would hold the loop.
        kwargs = await asyncio.to_thread(self._build, method, path, query=query, json=json,
                                         form=form, files=files, timeout=timeout)
        attempt = 0
        while True:
            try:
                response = await self._http.request(headers=self._headers, **kwargs)
            except httpx.HTTPError as exc:
                wait = self._retry_in(attempt, method, exc=exc)
                if wait is None:
                    raise _wrap(exc) from exc
            else:
                wait = self._retry_in(attempt, method, response=response)
                if wait is None:
                    kind, value = self._parse(response)
                    return AsyncJob(self, value) if kind == "job" else value
            attempt += 1
            await asyncio.sleep(wait)

    async def close(self) -> None:
        if self._owns_http:
            await self._http.aclose()

    async def __aenter__(self) -> "AsyncDipsac":
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.close()
