"""
Validation for user-uploaded files (resumes).

Rules enforced for every upload:
- the extension must be on the endpoint's allow-list;
- the leading bytes must match that extension (a renamed .exe is rejected);
- at most ``max_bytes`` are ever read into memory (the stream is read with a
  hard cap instead of trusting the client's declared size);
- the client's filename is never used on disk: callers store the file under
  ``safe_stored_filename(ext)``, so path separators, ``..`` and drive letters in
  the original name cannot escape the upload directory.

Error messages are generic and never echo parser or OS exception text.
"""

from __future__ import annotations

import os
import uuid
from dataclasses import dataclass
from typing import Iterable, Optional

from fastapi import HTTPException, Request, UploadFile, status

MAX_RESUME_BYTES = 10 * 1024 * 1024
_READ_CHUNK = 64 * 1024
# multipart framing overhead allowed on top of the file itself
_MULTIPART_SLACK = 64 * 1024

_OLE_MAGIC = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"


def _is_text(head: bytes) -> bool:
    if b"\x00" in head:
        return False
    try:
        head.decode("utf-8")
    except UnicodeDecodeError as exc:
        # A multi-byte character cut at the end of the sniffed prefix is fine.
        return exc.start >= len(head) - 3
    return True


_SIGNATURES = {
    ".pdf": lambda head: head.startswith(b"%PDF-"),
    ".docx": lambda head: head.startswith(b"PK\x03\x04"),
    ".doc": lambda head: head.startswith(_OLE_MAGIC),
    ".png": lambda head: head.startswith(b"\x89PNG\r\n\x1a\n"),
    ".jpg": lambda head: head.startswith(b"\xff\xd8\xff"),
    ".jpeg": lambda head: head.startswith(b"\xff\xd8\xff"),
    ".txt": _is_text,
}


@dataclass(frozen=True)
class ValidatedUpload:
    content: bytes
    extension: str  # lower-case, with leading dot


def _bad_request(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


def _too_large(max_bytes: int) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        detail=f"File too large. Maximum size is {max_bytes // (1024 * 1024)}MB.",
    )


def file_extension(filename: Optional[str]) -> str:
    """Lower-case extension of the *basename*, handling both / and \\ separators."""
    base = (filename or "").replace("\\", "/").rsplit("/", 1)[-1]
    return os.path.splitext(base)[1].lower()


def safe_stored_filename(extension: str) -> str:
    """Server-generated name for storing an upload; never derived from client input."""
    if extension not in _SIGNATURES:
        raise ValueError(f"unsupported extension {extension!r}")
    return f"{uuid.uuid4().hex}{extension}"


def reject_oversized_request(request: Optional[Request], max_bytes: int = MAX_RESUME_BYTES) -> None:
    """Fail fast on a declared Content-Length that cannot fit the limit."""
    if request is None:
        return
    declared = request.headers.get("content-length")
    if declared and declared.isdigit() and int(declared) > max_bytes + _MULTIPART_SLACK:
        raise _too_large(max_bytes)


async def read_validated_upload(
    file: UploadFile,
    allowed_extensions: Iterable[str],
    max_bytes: int = MAX_RESUME_BYTES,
) -> ValidatedUpload:
    """Read an upload with a hard size cap and check its type by content."""
    allowed = {ext.lower() for ext in allowed_extensions}
    unknown = allowed - set(_SIGNATURES)
    if unknown:
        raise ValueError(f"no signature check for {sorted(unknown)}")

    extension = file_extension(file.filename)
    if extension not in allowed:
        pretty = ", ".join(sorted(ext.lstrip(".").upper() for ext in allowed))
        raise _bad_request(f"Invalid file type. Allowed: {pretty}")

    chunks = []
    total = 0
    while True:
        chunk = await file.read(_READ_CHUNK)
        if not chunk:
            break
        total += len(chunk)
        if total > max_bytes:
            raise _too_large(max_bytes)
        chunks.append(chunk)
    content = b"".join(chunks)

    return _check_content(content, extension)


def _check_content(content: bytes, extension: str) -> ValidatedUpload:
    if not content:
        raise _bad_request("Uploaded file is empty.")
    if not _SIGNATURES[extension](content[:512]):
        raise _bad_request("File content does not match its type.")
    return ValidatedUpload(content=content, extension=extension)


class UploadRejected(ValueError):
    """Raised by validate_upload_bytes; ``str(exc)`` is safe to show the user."""


def validate_upload_bytes(
    filename: Optional[str],
    content: bytes,
    allowed_extensions: Iterable[str],
    max_bytes: int = MAX_RESUME_BYTES,
) -> ValidatedUpload:
    """Same rules as read_validated_upload, for payloads that are already in memory
    (e.g. base64 resumes sent over the interview WebSocket)."""
    allowed = {ext.lower() for ext in allowed_extensions}
    extension = file_extension(filename)
    try:
        if extension not in allowed:
            pretty = ", ".join(sorted(ext.lstrip(".").upper() for ext in allowed))
            raise _bad_request(f"Invalid file type. Allowed: {pretty}")
        if len(content) > max_bytes:
            raise _too_large(max_bytes)
        return _check_content(content, extension)
    except HTTPException as exc:
        raise UploadRejected(exc.detail) from None


def max_base64_length(max_bytes: int = MAX_RESUME_BYTES) -> int:
    """Longest base64 string that can decode to at most ``max_bytes``."""
    return 4 * ((max_bytes + 2) // 3)
