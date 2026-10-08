"""The official Python library for the DIPSAC API.

    from dipsac import Dipsac

    client = Dipsac(api_key="dps_...")            # or set DIPSAC_API_KEY
    client.pdf.merge(["a.pdf", "b.pdf"]).save("merged.pdf")

Docs: https://dipsac.com/dashboard/reference
"""
from ._client import DEFAULT_BASE_URL, AsyncDipsac, Dipsac
from ._errors import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    ConflictError,
    DipsacError,
    InternalServerError,
    JobFailedError,
    JobTimeoutError,
    NotFoundError,
    PayloadTooLargeError,
    PaymentRequiredError,
    PermissionDeniedError,
    RateLimitError,
    UnprocessableEntityError,
    UnsupportedMediaTypeError,
)
from ._files import FileInput
from ._models import AsyncJob, DipsacFile, Job
from ._version import __version__

__all__ = [
    "Dipsac", "AsyncDipsac", "DipsacFile", "Job", "AsyncJob", "FileInput", "DEFAULT_BASE_URL",
    "DipsacError", "APIConnectionError", "APITimeoutError", "APIStatusError", "BadRequestError",
    "AuthenticationError", "PaymentRequiredError", "PermissionDeniedError", "NotFoundError",
    "ConflictError", "PayloadTooLargeError", "UnsupportedMediaTypeError",
    "UnprocessableEntityError", "RateLimitError", "InternalServerError", "JobFailedError",
    "JobTimeoutError", "__version__",
]
