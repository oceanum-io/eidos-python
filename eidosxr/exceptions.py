"""Exceptions for the ``eidosxr`` package."""

from __future__ import annotations

from typing import Any, Optional


class EidosError(Exception):
    """Base class for eidos exceptions."""


class EidosSpecError(EidosError):
    """Base class for eidos spec exceptions."""


class EidosApiError(EidosError):
    """An error returned by the EIDOS platform API.

    Attributes:
        status: HTTP status code.
        error: the machine-readable ``error`` code from the response body.
        message: human-readable message (the response ``message`` when present).
        extra: any additional fields the endpoint returned (e.g.
            ``current_version`` on 412, ``bytes_remaining`` on 402,
            ``details`` on an invalid patch). These are also exposed as
            attributes, so ``err.current_version`` works.
    """

    #: default status for the subclass; overridden by the instance value.
    status: Optional[int] = None

    def __init__(
        self,
        message: str,
        *,
        status: Optional[int] = None,
        error: Optional[str] = None,
        **extra: Any,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error = error
        if status is not None:
            self.status = status
        self.extra = extra

    def __getattr__(self, item: str) -> Any:  # surface extra fields as attributes
        try:
            return self.__dict__["extra"][item]
        except KeyError as exc:  # pragma: no cover - defensive
            raise AttributeError(item) from exc


class BadRequest(EidosApiError):
    """400 — malformed request (invalid JSON, bad fields)."""

    status = 400


class InvalidPatch(BadRequest):
    """400 ``invalid_patch`` — the JSON Patch failed validation before apply.

    ``.details`` holds the per-operation validation errors.
    """


class Unauthorized(EidosApiError):
    """401 — missing or invalid credentials."""

    status = 401


class QuotaExceeded(EidosApiError):
    """402 ``quota_exceeded`` — storage/spec quota exhausted.

    ``.bytes_remaining`` is present on ingestion finalize failures.
    """

    status = 402


class Forbidden(EidosApiError):
    """403 — authenticated but not permitted (ownership, scope, spec binding)."""

    status = 403


class NotFound(EidosApiError):
    """404 — the resource does not exist or is not visible to the caller."""

    status = 404


class PatchConflict(EidosApiError):
    """409 ``patch_conflict`` — the JSON Patch could not be applied to the
    current specification (a referenced path no longer matches)."""

    status = 409


class Conflict(EidosApiError):
    """409 ``conflict`` — the resource is not in a state that accepts the write
    (e.g. writing to a dataset zarr store that is not ``processing``)."""

    status = 409


class LengthRequired(EidosApiError):
    """411 — a ``Content-Length`` header is required (ingestion zarr PUT)."""

    status = 411


class PreconditionFailed(EidosApiError):
    """412 ``precondition_failed`` — the ``If-Match`` version did not match the
    server. ``.current_version`` holds the live version to retry against."""

    status = 412


class PayloadTooLarge(EidosApiError):
    """413 — the request body exceeds the server limit (ingestion 64 MiB)."""

    status = 413


class RateLimited(EidosApiError):
    """429 ``rate_limited`` — too many requests. ``.retry_after`` (seconds) may
    be present."""

    status = 429


class ServerError(EidosApiError):
    """5xx — an error on the EIDOS platform."""

    status = 500


# error-code -> exception class, for the statuses that carry several distinct
# ``error`` codes.
_ERROR_CODES = {
    "invalid_patch": InvalidPatch,
    "patch_conflict": PatchConflict,
    "conflict": Conflict,
    "quota_exceeded": QuotaExceeded,
    "rate_limited": RateLimited,
    "precondition_failed": PreconditionFailed,
}

_STATUS_CLASSES = {
    400: BadRequest,
    401: Unauthorized,
    402: QuotaExceeded,
    403: Forbidden,
    404: NotFound,
    409: Conflict,
    411: LengthRequired,
    412: PreconditionFailed,
    413: PayloadTooLarge,
    429: RateLimited,
}


def error_from_response(response) -> EidosApiError:
    """Build the most specific :class:`EidosApiError` for a failed HTTP response."""
    status = response.status_code
    error = None
    message = None
    extra: dict = {}
    try:
        body = response.json()
    except ValueError:
        body = None
    if isinstance(body, dict):
        error = body.get("error")
        message = body.get("message")
        extra = {k: v for k, v in body.items() if k not in ("error", "message")}

    cls = _ERROR_CODES.get(error or "")
    if cls is None:
        cls = _STATUS_CLASSES.get(status)
    if cls is None:
        cls = ServerError if status >= 500 else EidosApiError

    if status == 429 and "retry_after" not in extra:
        retry = response.headers.get("Retry-After")
        if retry is not None:
            extra["retry_after"] = retry

    return cls(
        message or error or f"HTTP {status}",
        status=status,
        error=error,
        **extra,
    )
