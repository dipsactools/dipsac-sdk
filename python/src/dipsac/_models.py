"""What a call hands back when the answer is not plain JSON: a file, or a job."""
from __future__ import annotations

import asyncio
import os
import re
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Mapping, Optional, Union
from urllib.parse import unquote

from ._errors import JobFailedError, JobTimeoutError

if TYPE_CHECKING:
    from ._client import AsyncDipsac, Dipsac

# The API's own words for where a job is. Two families share these classes:
# /v1 jobs end in "succeeded", speech jobs in "done".
_FINISHED = ("succeeded", "done")
_FAILED = ("failed",)


def filename_from(headers: Mapping[str, str]) -> Optional[str]:
    """The name in a Content-Disposition header, preferring the UTF-8 form."""
    raw = headers.get("content-disposition") or ""
    star = re.search(r"filename\*\s*=\s*(?:UTF-8|utf-8)''([^;]+)", raw)
    if star:
        return os.path.basename(unquote(star.group(1).strip()))
    plain = re.search(r'filename\s*=\s*"([^"]*)"', raw) or re.search(r"filename\s*=\s*([^;]+)", raw)
    return os.path.basename(plain.group(1).strip()) if plain else None


class DipsacFile:
    """A file the API returned.

    Attributes:
        content: the bytes.
        content_type: e.g. ``application/pdf``.
        filename: the name the API gave it, when it gave one.
        headers: the response headers (lower-case names). Tools report extra
            facts here, e.g. ``x-generation-id`` on synthesised speech.
    """

    def __init__(self, content: bytes, *, content_type: str = "application/octet-stream",
                 filename: Optional[str] = None, headers: Optional[Mapping[str, str]] = None) -> None:
        self.content = content
        self.content_type = content_type
        self.filename = filename
        self.headers: Dict[str, str] = {k.lower(): v for k, v in (headers or {}).items()}

    @property
    def size(self) -> int:
        return len(self.content)

    @property
    def text(self) -> str:
        """The content as text (subtitles, for one)."""
        return self.content.decode("utf-8", errors="replace")

    def save(self, path: Union[str, "os.PathLike[str]", None] = None) -> Path:
        """Write the file and return where it went.

        With no path it is written to the current directory under the name the
        API gave it. A path that is an existing directory gets that name inside it.
        """
        name = self.filename or "download"
        target = Path(name) if path is None else Path(os.fspath(path))
        if target.is_dir():
            target = target / name
        target.write_bytes(self.content)
        return target

    def __bytes__(self) -> bytes:
        return self.content

    def __len__(self) -> int:
        return len(self.content)

    def __repr__(self) -> str:
        return f"<DipsacFile {self.filename or '(unnamed)'} {self.content_type} {self.size} bytes>"


class _JobState:
    """What both kinds of job know about themselves."""

    def __init__(self, data: Mapping[str, Any]) -> None:
        self.raw: Dict[str, Any] = dict(data)
        self.id: str = str(data.get("job_id") or data.get("id") or "")
        self._status_path: str = str(data.get("status_url") or data.get("poll") or f"/v1/jobs/{self.id}")

    @property
    def status(self) -> str:
        """queued, running, then succeeded (speech: done) or failed."""
        return str(self.raw.get("status") or "queued")

    @property
    def finished(self) -> bool:
        return self.status in _FINISHED

    @property
    def failed(self) -> bool:
        return self.status in _FAILED

    @property
    def error(self) -> Optional[str]:
        return self.raw.get("error")

    def _result_path(self) -> str:
        path = self.raw.get("result_url") or self.raw.get("audio_url")
        if path:
            return str(path)
        return f"{self._status_path.rstrip('/')}/result"

    def _absorb(self, data: Any) -> None:
        if isinstance(data, dict):
            self.raw.update(data)

    def _fail(self) -> JobFailedError:
        return JobFailedError(self.error or f"Job {self.id} failed.", job=self)

    def _late(self, waited: float) -> JobTimeoutError:
        return JobTimeoutError(
            f"Job {self.id} was still {self.status} after {waited:.0f} seconds. It was not "
            f"cancelled; call wait() again, or fetch it later by its id.", job=self)

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {self.id} {self.status}>"


class Job(_JobState):
    """Work the API is doing in the background.

        job = client.video.convert("in.mov", "mp4", mode="async")
        clip = job.wait()          # polls until it is done, then downloads
        clip.save("out.mp4")
    """

    def __init__(self, client: "Dipsac", data: Mapping[str, Any]) -> None:
        super().__init__(data)
        self._client = client

    def refresh(self) -> "Job":
        """Ask the API where the job is now."""
        self._absorb(self._client._request("GET", self._status_path))
        return self

    def result(self) -> DipsacFile:
        """Download the output of a finished job."""
        return self._client._request("GET", self._result_path())

    def wait(self, *, timeout: float = 600.0, poll_interval: float = 2.0) -> DipsacFile:
        """Wait for the job and return its output.

        Raises JobFailedError if the job fails and JobTimeoutError if it is not
        done within ``timeout`` seconds.
        """
        started = time.monotonic()
        while True:
            self.refresh()
            if self.finished:
                return self.result()
            if self.failed:
                raise self._fail()
            waited = time.monotonic() - started
            if waited + poll_interval > timeout:
                raise self._late(waited)
            time.sleep(poll_interval)


class AsyncJob(_JobState):
    """Work the API is doing in the background, for AsyncDipsac."""

    def __init__(self, client: "AsyncDipsac", data: Mapping[str, Any]) -> None:
        super().__init__(data)
        self._client = client

    async def refresh(self) -> "AsyncJob":
        self._absorb(await self._client._request("GET", self._status_path))
        return self

    async def result(self) -> DipsacFile:
        return await self._client._request("GET", self._result_path())

    async def wait(self, *, timeout: float = 600.0, poll_interval: float = 2.0) -> DipsacFile:
        started = time.monotonic()
        while True:
            await self.refresh()
            if self.finished:
                return await self.result()
            if self.failed:
                raise self._fail()
            waited = time.monotonic() - started
            if waited + poll_interval > timeout:
                raise self._late(waited)
            await asyncio.sleep(poll_interval)
