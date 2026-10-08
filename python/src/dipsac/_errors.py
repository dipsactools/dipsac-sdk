"""Everything this library raises.

    DipsacError
    ├── APIConnectionError        the request never got an answer
    │   └── APITimeoutError
    ├── APIStatusError            the API answered with an error
    │   ├── BadRequestError            400
    │   ├── AuthenticationError        401  the key is missing or wrong
    │   ├── PaymentRequiredError       402  an allowance is used up
    │   ├── PermissionDeniedError      403  the plan does not include this
    │   ├── NotFoundError              404
    │   ├── ConflictError              409  e.g. a job that has not finished
    │   ├── PayloadTooLargeError       413
    │   ├── UnsupportedMediaTypeError  415  the wrong kind of file
    │   ├── UnprocessableEntityError   422  a parameter is missing or invalid
    │   ├── RateLimitError             429
    │   └── InternalServerError        500 and above
    ├── JobFailedError            a background job ended in failure
    └── JobTimeoutError           wait() ran out of time; the job may still finish
"""
from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional


class DipsacError(Exception):
    """Base class of every error raised by this library."""


class APIConnectionError(DipsacError):
    """The API could not be reached, or the connection broke before an answer."""


class APITimeoutError(APIConnectionError):
    """No answer arrived within the timeout."""


class APIStatusError(DipsacError):
    """The API answered with an error status.

    Attributes:
        status_code: the HTTP status.
        code: the API's short name for the error, e.g. ``rate_limited``.
        message: the API's sentence about it.
        request_id: quote this to DIPSAC support.
        body: the whole response body, parsed if it was JSON.
        headers: the response headers (lower-case names).
    """

    def __init__(self, message: str, *, status_code: int, code: Optional[str] = None,
                 request_id: Optional[str] = None, body: Any = None,
                 headers: Optional[Mapping[str, str]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.request_id = request_id
        self.body = body
        self.headers: Dict[str, str] = dict(headers or {})

    def __str__(self) -> str:
        bits = [f"{self.status_code}"]
        if self.code:
            bits.append(self.code)
        text = f"[{' '.join(bits)}] {self.message}"
        return f"{text} (request_id {self.request_id})" if self.request_id else text

    def _field(self, name: str) -> Any:
        return self.body.get(name) if isinstance(self.body, dict) else None


class BadRequestError(APIStatusError):
    pass


class AuthenticationError(APIStatusError):
    pass


class PaymentRequiredError(APIStatusError):
    """An allowance or quota is used up; the body carries the numbers."""


class PermissionDeniedError(APIStatusError):
    """The key's plan does not include this endpoint."""

    @property
    def required_plan(self) -> Optional[str]:
        return self._field("required_plan")

    @property
    def current_plan(self) -> Optional[str]:
        return self._field("current_plan")


class NotFoundError(APIStatusError):
    pass


class ConflictError(APIStatusError):
    pass


class PayloadTooLargeError(APIStatusError):
    pass


class UnsupportedMediaTypeError(APIStatusError):
    @property
    def accepted(self) -> Optional[List[str]]:
        """The file types this endpoint takes."""
        return self._field("accepted")


class UnprocessableEntityError(APIStatusError):
    @property
    def fields(self) -> Optional[List[Dict[str, Any]]]:
        """Which parameters were refused, and why."""
        return self._field("fields")


class RateLimitError(APIStatusError):
    """Too many requests.

    ``retry_after`` is how many seconds the API asked to wait. A second or two
    is the per-second limit; a day is the plan's monthly limit, used up.
    """

    @property
    def retry_after(self) -> Optional[float]:
        raw = self.headers.get("retry-after")
        try:
            return float(raw) if raw is not None else None
        except ValueError:
            return None


class InternalServerError(APIStatusError):
    pass


class JobFailedError(DipsacError):
    """A background job ended in failure. ``job`` is the job, with its last status."""

    def __init__(self, message: str, job: Any = None) -> None:
        super().__init__(message)
        self.job = job


class JobTimeoutError(DipsacError):
    """wait() gave up. The job itself was not cancelled and may still finish."""

    def __init__(self, message: str, job: Any = None) -> None:
        super().__init__(message)
        self.job = job


_BY_STATUS = {
    400: BadRequestError, 401: AuthenticationError, 402: PaymentRequiredError,
    403: PermissionDeniedError, 404: NotFoundError, 409: ConflictError,
    413: PayloadTooLargeError, 415: UnsupportedMediaTypeError,
    422: UnprocessableEntityError, 429: RateLimitError,
}


def error_for(status_code: int, body: Any, headers: Mapping[str, str]) -> APIStatusError:
    """The right exception for an error response."""
    lowered = {k.lower(): v for k, v in headers.items()}
    code = message = request_id = None
    if isinstance(body, dict):
        code = body.get("error") if isinstance(body.get("error"), str) else None
        for key in ("message", "detail"):
            if isinstance(body.get(key), str) and body[key]:
                message = body[key]
                break
        request_id = body.get("request_id") if isinstance(body.get("request_id"), str) else None
    elif isinstance(body, str) and body.strip():
        message = body.strip()[:500]
    request_id = request_id or lowered.get("x-request-id")
    cls = _BY_STATUS.get(status_code) or (InternalServerError if status_code >= 500 else APIStatusError)
    return cls(message or f"The API answered {status_code}.", status_code=status_code, code=code,
               request_id=request_id, body=body, headers=lowered)
