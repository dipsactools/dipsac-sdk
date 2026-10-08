"""Turning what a caller hands over into one part of an upload.

A file may be given as:

    "report.pdf" or Path("report.pdf")     a path; the file is read
    open("report.pdf", "rb")               an open binary file
    b"%PDF-1.7 ..."                        the bytes themselves
    ("report.pdf", data)                   a name and bytes (or an open file)
    ("report.pdf", data, "application/pdf")

THE NAME MATTERS. The API decides what a file is by the extension of its name
and refuses one it does not expect ("'file' has unsupported type"). A path and
an open file carry their own name. Bare bytes carry none, so their type is read
from how they begin (PDF, PNG, JPEG, GIF, WebP, WAV, MP3, MP4, OGG, FLAC, WebM
and GLB are recognised); for anything else, a Word file for one, pass the tuple
form.

EVERY UPLOAD IS READ INTO MEMORY BEFORE IT IS SENT. The API requires a
Content-Length on uploads and answers 411 to a chunked body, and a length is
only certain once the bytes are in hand.
"""
from __future__ import annotations

import mimetypes
import os
from typing import IO, Any, Optional, Tuple, Union

FileContent = Union[bytes, bytearray, memoryview, IO[bytes]]
FileInput = Union[
    str,
    "os.PathLike[str]",
    bytes,
    bytearray,
    memoryview,
    IO[bytes],
    Tuple[str, FileContent],
    Tuple[str, FileContent, str],
]

_MAGIC = (
    (b"%PDF", "pdf"), (b"\x89PNG\r\n\x1a\n", "png"), (b"\xff\xd8\xff", "jpg"),
    (b"GIF87a", "gif"), (b"GIF89a", "gif"), (b"ID3", "mp3"), (b"\xff\xfb", "mp3"),
    (b"\xff\xf3", "mp3"), (b"OggS", "ogg"), (b"fLaC", "flac"), (b"glTF", "glb"),
    (b"\x1a\x45\xdf\xa3", "webm"),
)


def _sniff(head: bytes) -> Optional[str]:
    """An extension for bytes that came with no name, or None."""
    for magic, ext in _MAGIC:
        if head.startswith(magic):
            return ext
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return "webp"
    if head[:4] == b"RIFF" and head[8:12] == b"WAVE":
        return "wav"
    if head[4:8] == b"ftyp":
        return "mp4"
    return None


def _read(content: Any) -> bytes:
    if isinstance(content, (bytes, bytearray, memoryview)):
        return bytes(content)
    if hasattr(content, "read"):
        data = content.read()
        if isinstance(data, str):
            raise TypeError("a file must be opened in binary mode ('rb'), not text mode")
        return bytes(data)
    raise TypeError(f"cannot upload a {type(content).__name__}; pass a path, bytes, "
                    f"an open binary file, or a (filename, content) tuple")


def to_part(value: Any, field: str = "file") -> Tuple[str, bytes, str]:
    """(filename, bytes, content type) for one uploaded file."""
    filename: Optional[str] = None
    content_type: Optional[str] = None
    if isinstance(value, tuple):
        if len(value) == 2:
            filename, content = value
        elif len(value) == 3:
            filename, content, content_type = value
        else:
            raise TypeError("a file tuple is (filename, content) or (filename, content, content_type)")
        data = _read(content)
    elif isinstance(value, (str, os.PathLike)):
        path = os.fspath(value)
        with open(path, "rb") as fh:
            data = fh.read()
        filename = os.path.basename(path)
    else:
        data = _read(value)
        name = getattr(value, "name", None)
        if isinstance(name, str) and name and not name.startswith("<"):
            filename = os.path.basename(name)
    if not filename:
        ext = _sniff(data[:16])
        filename = f"{field}.{ext}" if ext else field
    if not content_type:
        content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    return str(filename), data, content_type
