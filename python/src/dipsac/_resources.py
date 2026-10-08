"""The API's operations, one method each. GENERATED: do not edit.

Written by codegen/generate.py from openapi/dipsac.openapi.json. To change
a method, change the schema snapshot (or the tables in the generator) and
run it again.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Literal, Optional, Sequence, Union
from urllib.parse import quote

from ._files import FileInput
from ._models import AsyncJob, DipsacFile, Job

if TYPE_CHECKING:
    from ._client import AsyncDipsac, Dipsac


def _seg(value: Any) -> str:
    """One path segment, escaped."""
    return quote(str(value), safe="")


class _Resource:
    def __init__(self, client: "Dipsac") -> None:
        self._client = client


class _AsyncResource:
    def __init__(self, client: "AsyncDipsac") -> None:
        self._client = client



class Pdf(_Resource):
    """PDF tools: merge, split, compress, convert, protect, watermark."""

    def merge(
        self,
        files: Sequence[FileInput],
        *,
        page_filter: Optional[str] = None,
        pdf_filter: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> DipsacFile:
        """Merge several PDFs into one.

        Args:
            files: Two or more PDF files, merged in the order given
            page_filter: Pages to take from each file: all | odd | even (server default:
                'all')
            pdf_filter: Which files to include by position: all | odd | even (server
                default: 'all')
        """
        return self._client._request(
            "POST",
            "/v1/pdf/merge",
            files={"files": files},
            form={"page_filter": page_filter, "pdf_filter": pdf_filter},
            multipart=True,
            timeout=timeout,
        )

    def split(
        self,
        file: FileInput,
        pages: str,
        *,
        timeout: Optional[float] = None,
    ) -> DipsacFile:
        """Extract a page range into a new PDF.

        Args:
            file: The PDF to take pages from
            pages: 1-indexed selection, e.g. '1-3,5,9-'
        """
        return self._client._request(
            "POST",
            "/v1/pdf/split",
            files={"file": file},
            form={"pages": pages},
            multipart=True,
            timeout=timeout,
        )

    def delete_pages(
        self,
        file: FileInput,
        pages: str,
        *,
        timeout: Optional[float] = None,
    ) -> DipsacFile:
        """Remove pages from a PDF.

        Args:
            pages: 1-indexed selection to delete, e.g. '2,4-6'
        """
        return self._client._request(
            "POST",
            "/v1/pdf/delete-pages",
            files={"file": file},
            form={"pages": pages},
            multipart=True,
            timeout=timeout,
        )

    def rotate(
        self,
        file: FileInput,
        *,
        degrees: Optional[int] = None,
        pages: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> DipsacFile:
        """Rotate pages.

        Args:
            degrees: Clockwise rotation: 90, 180 or 270 (server default: 90)
            pages: Optional 1-indexed selection; blank rotates every page
        """
        return self._client._request(
            "POST",
            "/v1/pdf/rotate",
            files={"file": file},
            form={"degrees": degrees, "pages": pages},
            multipart=True,
            timeout=timeout,
        )

    def compress(
        self,
        file: FileInput,
        *,
        preset: Optional[str] = None,
        remove_metadata: Optional[bool] = None,
        mode: Optional[Literal['sync', 'async']] = None,
        timeout: Optional[float] = None,
    ) -> Union[DipsacFile, Job]:
        """Reduce PDF file size.

        Args:
            preset: screen | ebook | printer | prepress — smaller to larger (server default:
                'ebook')
            remove_metadata: Strip document metadata (server default: True)
            mode: 'async' returns a job id instead of the file (server default: 'sync')

        Returns a Job instead of the result when the work is sent to the
        background; call its wait() for the result.
        """
        return self._client._request(
            "POST",
            "/v1/pdf/compress",
            files={"file": file},
            form={"preset": preset, "remove_metadata": remove_metadata, "mode": mode},
            multipart=True,
            timeout=timeout,
        )

    def convert(
        self,
        file: FileInput,
        output_format: str,
        *,
        mode: Optional[Literal['sync', 'async']] = None,
        timeout: Optional[float] = None,
    ) -> Union[DipsacFile, Job]:
        """Convert a PDF to Word, Excel or PowerPoint.

        `xlsx` extracts detected tables — it is not a full-page conversion, and a PDF with
        no tables is an error rather than an empty workbook. `docx` needs a real text layer,
        so scanned pages will not convert.

        Args:
            output_format: docx | xlsx | pptx
            mode: 'async' returns a job id instead of the file (server default: 'sync')

        Returns a Job instead of the result when the work is sent to the
        background; call its wait() for the result.
        """
        return self._client._request(
            "POST",
            "/v1/pdf/convert",
            files={"file": file},
            form={"output_format": output_format, "mode": mode},
            multipart=True,
            timeout=timeout,
        )

    def from_office(
        self,
        file: FileInput,
        *,
        timeout: Optional[float] = None,
    ) -> DipsacFile:
        """Create a PDF from a Word or Excel file.

        Args:
            file: A .docx or .xlsx file
        """
        return self._client._request(
            "POST",
            "/v1/pdf/from-office",
            files={"file": file},
            multipart=True,
            timeout=timeout,
        )

    def protect(
        self,
        file: FileInput,
        password: str,
        *,
        owner_password: Optional[str] = None,
        allow_printing: Optional[bool] = None,
        allow_copying: Optional[bool] = None,
        timeout: Optional[float] = None,
    ) -> DipsacFile:
        """Password-protect a PDF.

        Args:
            password: Password needed to open the file
            owner_password: Password needed to change permissions; defaults to `password`
        """
        return self._client._request(
            "POST",
            "/v1/pdf/protect",
            files={"file": file},
            form={"password": password, "owner_password": owner_password, "allow_printing": allow_printing, "allow_copying": allow_copying},
            multipart=True,
            timeout=timeout,
        )

    def unlock(
        self,
        file: FileInput,
        *,
        password: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> DipsacFile:
        """Remove password protection.

        Args:
            password: The document's current open password
        """
        return self._client._request(
            "POST",
            "/v1/pdf/unlock",
            files={"file": file},
            form={"password": password},
            multipart=True,
            timeout=timeout,
        )

    def watermark(
        self,
        file: FileInput,
        *,
        text: Optional[str] = None,
        opacity: Optional[float] = None,
        font_size: Optional[int] = None,
        color: Optional[str] = None,
        position: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> DipsacFile:
        """Stamp a watermark across every page.

        Args:
            color: Hex colour, e.g. #FF0000 (server default: '#FF0000')
            position: diagonal | center | top | bottom (server default: 'diagonal')
        """
        return self._client._request(
            "POST",
            "/v1/pdf/watermark",
            files={"file": file},
            form={"text": text, "opacity": opacity, "font_size": font_size, "color": color, "position": position},
            multipart=True,
            timeout=timeout,
        )

    def metadata(
        self,
        file: FileInput,
        *,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Read a PDF's metadata.
        """
        return self._client._request(
            "POST",
            "/v1/pdf/metadata",
            files={"file": file},
            multipart=True,
            timeout=timeout,
        )


class Image(_Resource):
    """Image tools: convert, compress, resize, crop, remove a background."""

    def convert(
        self,
        file: FileInput,
        output_format: str,
        *,
        quality: Optional[int] = None,
        background: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> DipsacFile:
        """Convert an image to another format.

        Args:
            file: Any supported image; the input format is detected
            output_format: png | jpg | webp | bmp | tiff | gif | avif | heic
            quality: Ignored by lossless formats (server default: 85)
            background: Fill for transparency when the target has no alpha channel (server
                default: '#FFFFFF')
        """
        return self._client._request(
            "POST",
            "/v1/image/convert",
            files={"file": file},
            form={"output_format": output_format, "quality": quality, "background": background},
            multipart=True,
            timeout=timeout,
        )

    def compress(
        self,
        file: FileInput,
        *,
        quality: Optional[int] = None,
        timeout: Optional[float] = None,
    ) -> DipsacFile:
        """Re-encode an image at a lower quality.

        Keeps the input format. A PNG is re-encoded losslessly with optimisation, so
        `quality` has no effect on it — use `/v1/image/convert` to WebP or AVIF if you want
        a real size drop on a PNG.
        """
        return self._client._request(
            "POST",
            "/v1/image/compress",
            files={"file": file},
            form={"quality": quality},
            multipart=True,
            timeout=timeout,
        )

    def resize(
        self,
        file: FileInput,
        *,
        width: Optional[int] = None,
        height: Optional[int] = None,
        fit: Optional[str] = None,
        quality: Optional[int] = None,
        timeout: Optional[float] = None,
    ) -> DipsacFile:
        """Resize an image.

        Args:
            width: 0 means derive from height (server default: 0)
            height: 0 means derive from width (server default: 0)
            fit: contain (keep aspect, fit inside) | cover (crop to fill) | exact (stretch)
                (server default: 'contain')
        """
        return self._client._request(
            "POST",
            "/v1/image/resize",
            files={"file": file},
            form={"width": width, "height": height, "fit": fit, "quality": quality},
            multipart=True,
            timeout=timeout,
        )

    def crop(
        self,
        file: FileInput,
        x: int,
        y: int,
        width: int,
        height: int,
        *,
        quality: Optional[int] = None,
        timeout: Optional[float] = None,
    ) -> DipsacFile:
        """Crop a rectangle out of an image.

        Args:
            x: Left edge in pixels
            y: Top edge in pixels
        """
        return self._client._request(
            "POST",
            "/v1/image/crop",
            files={"file": file},
            form={"x": x, "y": y, "width": width, "height": height, "quality": quality},
            multipart=True,
            timeout=timeout,
        )

    def remove_background(
        self,
        file: FileInput,
        *,
        output_format: Optional[str] = None,
        background: Optional[str] = None,
        mode: Optional[Literal['sync', 'async']] = None,
        timeout: Optional[float] = None,
    ) -> Union[DipsacFile, Job]:
        """Cut the subject out of a photo.

        Runs a segmentation model, so it is markedly slower than the other image endpoints —
        seconds, not milliseconds. Use `mode=async` in bulk.

        Args:
            output_format: png keeps transparency; jpg flattens onto `background` (server
                default: 'png')
            mode: 'async' returns a job id instead of the file (server default: 'sync')

        Returns a Job instead of the result when the work is sent to the
        background; call its wait() for the result.
        """
        return self._client._request(
            "POST",
            "/v1/image/remove-background",
            files={"file": file},
            form={"output_format": output_format, "background": background, "mode": mode},
            multipart=True,
            timeout=timeout,
        )

    def to_pdf(
        self,
        files: Sequence[FileInput],
        *,
        timeout: Optional[float] = None,
    ) -> DipsacFile:
        """Combine images into a single PDF.

        Args:
            files: One or more images, one page each, in order
        """
        return self._client._request(
            "POST",
            "/v1/image/to-pdf",
            files={"files": files},
            multipart=True,
            timeout=timeout,
        )

    def info(
        self,
        file: FileInput,
        *,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Read an image's dimensions and format.
        """
        return self._client._request(
            "POST",
            "/v1/image/info",
            files={"file": file},
            multipart=True,
            timeout=timeout,
        )


class Audio(_Resource):
    """Audio tools: convert, normalise loudness, join files. Needs the Pro plan."""

    def convert(
        self,
        file: FileInput,
        output_format: str,
        *,
        mode: Optional[Literal['sync', 'async']] = None,
        timeout: Optional[float] = None,
    ) -> Union[DipsacFile, Job]:
        """Convert audio to another format.

        `amr` is narrowband by definition — the result is 8 kHz mono whatever went in.
        Everything else keeps the source sample rate and channels.

        Args:
            file: Any supported audio file
            output_format: mp3 | wav | ogg | aac | m4a | flac | amr

        Returns a Job instead of the result when the work is sent to the
        background; call its wait() for the result.
        """
        return self._client._request(
            "POST",
            "/v1/audio/convert",
            files={"file": file},
            form={"output_format": output_format, "mode": mode},
            multipart=True,
            timeout=timeout,
        )

    def normalize(
        self,
        file: FileInput,
        *,
        target_lufs: Optional[float] = None,
        mode: Optional[Literal['sync', 'async']] = None,
        timeout: Optional[float] = None,
    ) -> Union[DipsacFile, Job]:
        """Even out audio loudness.

        Args:
            target_lufs: Integrated loudness target; -14 LUFS matches most streaming
                platforms (server default: -14.0)

        Returns a Job instead of the result when the work is sent to the
        background; call its wait() for the result.
        """
        return self._client._request(
            "POST",
            "/v1/audio/normalize",
            files={"file": file},
            form={"target_lufs": target_lufs, "mode": mode},
            multipart=True,
            timeout=timeout,
        )

    def merge(
        self,
        files: Sequence[FileInput],
        *,
        timeout: Optional[float] = None,
    ) -> DipsacFile:
        """Join several audio files end to end.

        Args:
            files: Two or more audio files, joined in the order given
        """
        return self._client._request(
            "POST",
            "/v1/audio/merge",
            files={"files": files},
            multipart=True,
            timeout=timeout,
        )


class Video(_Resource):
    """Video tools: convert, trim, resize, mute, pull the audio out. Needs the Pro plan."""

    def convert(
        self,
        file: FileInput,
        output_format: str,
        *,
        mode: Optional[Literal['sync', 'async']] = None,
        timeout: Optional[float] = None,
    ) -> Union[DipsacFile, Job]:
        """Convert video to another container/codec.

        `webm` re-encodes with VP9, which is markedly slower than the H.264 targets. Use
        `mode=async` for anything longer than a short clip.

        Args:
            output_format: mp4 | avi | mkv | mov | webm

        Returns a Job instead of the result when the work is sent to the
        background; call its wait() for the result.
        """
        return self._client._request(
            "POST",
            "/v1/video/convert",
            files={"file": file},
            form={"output_format": output_format, "mode": mode},
            multipart=True,
            timeout=timeout,
        )

    def extract_audio(
        self,
        file: FileInput,
        *,
        output_format: Optional[str] = None,
        mode: Optional[Literal['sync', 'async']] = None,
        timeout: Optional[float] = None,
    ) -> Union[DipsacFile, Job]:
        """Pull the audio track out of a video.

        Args:
            output_format: mp3 | wav | ogg | aac | m4a | flac (server default: 'mp3')

        Returns a Job instead of the result when the work is sent to the
        background; call its wait() for the result.
        """
        return self._client._request(
            "POST",
            "/v1/video/extract-audio",
            files={"file": file},
            form={"output_format": output_format, "mode": mode},
            multipart=True,
            timeout=timeout,
        )

    def cut(
        self,
        file: FileInput,
        end: str,
        *,
        start: Optional[str] = None,
        mode: Optional[Literal['sync', 'async']] = None,
        timeout: Optional[float] = None,
    ) -> Union[DipsacFile, Job]:
        """Trim a video to a time range.

        Args:
            end: Seconds or timestamp; must be after start
            start: Seconds (12.5) or timestamp (00:01:30) (server default: '0')

        Returns a Job instead of the result when the work is sent to the
        background; call its wait() for the result.
        """
        return self._client._request(
            "POST",
            "/v1/video/cut",
            files={"file": file},
            form={"start": start, "end": end, "mode": mode},
            multipart=True,
            timeout=timeout,
        )

    def resize(
        self,
        file: FileInput,
        *,
        width: Optional[int] = None,
        height: Optional[int] = None,
        mode: Optional[Literal['sync', 'async']] = None,
        timeout: Optional[float] = None,
    ) -> Union[DipsacFile, Job]:
        """Scale a video to a new width/height.

        Args:
            width: 0 derives from height, keeping aspect (server default: 0)
            height: 0 derives from width, keeping aspect (server default: 0)

        Returns a Job instead of the result when the work is sent to the
        background; call its wait() for the result.
        """
        return self._client._request(
            "POST",
            "/v1/video/resize",
            files={"file": file},
            form={"width": width, "height": height, "mode": mode},
            multipart=True,
            timeout=timeout,
        )

    def mute(
        self,
        file: FileInput,
        *,
        mode: Optional[Literal['sync', 'async']] = None,
        timeout: Optional[float] = None,
    ) -> Union[DipsacFile, Job]:
        """Strip the audio track from a video.

        Returns a Job instead of the result when the work is sent to the
        background; call its wait() for the result.
        """
        return self._client._request(
            "POST",
            "/v1/video/mute",
            files={"file": file},
            form={"mode": mode},
            multipart=True,
            timeout=timeout,
        )


class Seo(_Resource):
    """SEO checks: meta tags, TLS certificate, redirects, WHOIS, canonical."""

    def meta(
        self,
        title: str,
        description: str,
        url: str,
        *,
        image: Optional[str] = None,
        site_name: Optional[str] = None,
        keywords: Optional[str] = None,
        author: Optional[str] = None,
        twitter_card: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Generate meta and Open Graph tags.

        Produces the `<meta>`, Open Graph and Twitter Card block for a page.

        Args:
            url: Canonical URL of the page
            image: Absolute URL of the social preview image
            twitter_card: summary | summary_large_image | app | player (server default:
                'summary_large_image')
        """
        return self._client._request(
            "POST",
            "/v1/seo/meta",
            json={"title": title, "description": description, "url": url, "image": image, "site_name": site_name, "keywords": keywords, "author": author, "twitter_card": twitter_card},
            timeout=timeout,
        )

    def ssl(
        self,
        url: str,
        *,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Inspect a site's TLS certificate.

        Args:
            url: Domain or URL, e.g. example.com
        """
        return self._client._request(
            "GET",
            "/v1/seo/ssl",
            query={"url": url},
            timeout=timeout,
        )

    def redirects(
        self,
        url: str,
        *,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Follow a URL's redirect chain.

        Args:
            url: The starting URL
        """
        return self._client._request(
            "GET",
            "/v1/seo/redirects",
            query={"url": url},
            timeout=timeout,
        )

    def whois(
        self,
        url: str,
        *,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """WHOIS registration record for a domain.

        Args:
            url: Domain or URL
        """
        return self._client._request(
            "GET",
            "/v1/seo/whois",
            query={"url": url},
            timeout=timeout,
        )

    def domain_age(
        self,
        url: str,
        *,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """How long a domain has been registered.

        A projection of the WHOIS record — the registration and expiry dates and the age
        derived from them, without the rest of the record.

        Args:
            url: Domain or URL
        """
        return self._client._request(
            "GET",
            "/v1/seo/domain-age",
            query={"url": url},
            timeout=timeout,
        )

    def canonical(
        self,
        url: str,
        *,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Check a page's canonical URL.

        Args:
            url: The page to inspect
        """
        return self._client._request(
            "GET",
            "/v1/seo/canonical",
            query={"url": url},
            timeout=timeout,
        )


class Dev(_Resource):
    """Developer utilities: bcrypt hashing, JSON validation and formatting."""

    def hash(
        self,
        password: str,
        *,
        rounds: Optional[int] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Hash a password with bcrypt.

        The cost is the whole point of bcrypt, so it is a parameter rather than a constant.
        Note that it is exponential: `rounds=16` is 16x the CPU of `rounds=12` and takes a
        noticeable fraction of a second.

        Args:
            password: The plaintext to hash
            rounds: bcrypt cost. Each step doubles the work; 12 is Laravel's default (server
                default: 12)
        """
        return self._client._request(
            "POST",
            "/v1/dev/hash",
            json={"password": password, "rounds": rounds},
            timeout=timeout,
        )

    def hash_verify(
        self,
        password: str,
        hash: str,
        *,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Check a password against a bcrypt hash.

        A malformed hash is `matches: false`, not an error — telling the caller which of the
        two inputs was wrong is exactly what an attacker wants.

        Args:
            hash: A bcrypt hash to check against
        """
        return self._client._request(
            "POST",
            "/v1/dev/hash/verify",
            json={"password": password, "hash": hash},
            timeout=timeout,
        )

    def json(
        self,
        content: str,
        *,
        action: Optional[str] = None,
        indent: Optional[int] = None,
        sort_keys: Optional[bool] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Validate, format or minify JSON.

        A syntax error comes back as `valid: false` with the line and column, and HTTP 200 —
        the request itself was well-formed, and "this document is invalid" is the answer,
        not a failure to answer.

        Args:
            content: The JSON document, as text
            action: format | minify | validate (server default: 'format')
            indent: Spaces per level when action=format (server default: 2)
            sort_keys: Order object keys alphabetically (server default: False)
        """
        return self._client._request(
            "POST",
            "/v1/dev/json",
            json={"content": content, "action": action, "indent": indent, "sort_keys": sort_keys},
            timeout=timeout,
        )


class Glb(_Resource):
    """3D model (.glb) inspection and editing plans. Needs the Enterprise plan."""

    def limits(
        self,
        *,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Every limit of the GLB routes.

        The numbers the three routes below hold a request to: the largest scene description,
        how many operations one edit may carry, how many images and of what size, how long
        one request may run. Read it once and check before you send; the numbers can change
        without a new version of this API.
        """
        return self._client._request(
            "GET",
            "/v1/glb/limits",
            timeout=timeout,
        )

    def inspect(
        self,
        head: FileInput,
        size: int,
        *,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """What a .glb is, and what may be done to it.

        Send the model's **head** and its size; the model itself is never sent.

        Args:
            head: The first bytes of the .glb, as a file part: its 12-byte header, its JSON
                chunk, and the 8-byte header of the chunk after it. That is `file.slice(0, 20 +
                jsonLength + 8)`, where jsonLength is the little-endian uint32 at byte 12. Never
                the whole file
            size: The length of the whole .glb in bytes
        """
        return self._client._request(
            "POST",
            "/v1/glb/inspect",
            files={"head": head},
            form={"size": size},
            multipart=True,
            timeout=timeout,
        )

    def plan(
        self,
        head: FileInput,
        size: int,
        edit: str,
        *,
        images: Optional[Sequence[FileInput]] = None,
        hashes: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Compile edits to a .glb into a plan of byte ranges.

        Answers `{"segments": [...], "total": N, "report": {...}}`. **You build the edited
        file** by concatenating the segments in order:

        Args:
            head: The first bytes of the .glb, as a file part: its 12-byte header, its JSON
                chunk, and the 8-byte header of the chunk after it. That is `file.slice(0, 20 +
                jsonLength + 8)`, where jsonLength is the little-endian uint32 at byte 12. Never
                the whole file
            size: The length of the whole .glb in bytes
            edit: JSON: `{"ops": [...], "cleanup": {...}, "removal": "required" | "unlink",
                "mode": "plan" | "check"}`. An operation names things by their index in the file
                as it arrived
            images: PNG or JPEG file parts an operation puts into the model. Each part's
                FILENAME is the name an operation refers to it by
            hashes: JSON `{"<image index>": "<sha-256, 64 lowercase hex>"}`, each computed
                by the caller over the image's own bytes. Needed only when `cleanup.dedupe` is
                asked for
        """
        return self._client._request(
            "POST",
            "/v1/glb/plan",
            files={"head": head, "images": images},
            form={"size": size, "edit": edit, "hashes": hashes},
            multipart=True,
            timeout=timeout,
        )

    def image(
        self,
        image: FileInput,
        *,
        max_size: Optional[int] = None,
        jpeg_quality: Optional[int] = None,
        to_jpeg: Optional[bool] = None,
        timeout: Optional[float] = None,
    ) -> Any:
        """Shrink one texture.

        A smaller picture comes back as bytes (`image/png` or `image/jpeg`) with `X-Glb-*`
        headers saying what was done. A picture that was left alone comes back as JSON,
        `{"changed": false, "outcome": "..."}`, with one word saying why. The ranges
        `max_size` and `jpeg_quality` may take are in `GET /v1/glb/limits`.

        Args:
            image: One PNG or JPEG
            max_size: The longest side, in pixels, of the picture that comes back
            jpeg_quality: The quality a JPEG is written at
            to_jpeg: Allow a PNG with no transparency to come back as a JPEG. Only where
                inspect says `jpeg_allowed` for that image
        """
        return self._client._request(
            "POST",
            "/v1/glb/image",
            files={"image": image},
            form={"max_size": max_size, "jpeg_quality": jpeg_quality, "to_jpeg": to_jpeg},
            multipart=True,
            timeout=timeout,
        )


class Jobs(_Resource):
    """Status and result of work submitted with mode="async"."""

    def get(
        self,
        job_id: str,
        *,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Check the status of an async job.

        Poll this until `status` is `succeeded` or `failed`. A second or two between polls
        is plenty; the work is measured in seconds, not milliseconds.
        """
        return self._client._request(
            "GET",
            f"/v1/jobs/{_seg(job_id)}",
            timeout=timeout,
        )

    def result(
        self,
        job_id: str,
        *,
        timeout: Optional[float] = None,
    ) -> DipsacFile:
        """Download a finished job's output.
        """
        return self._client._request(
            "GET",
            f"/v1/jobs/{_seg(job_id)}/result",
            timeout=timeout,
        )


class Ai(_Resource):
    """AI Voice Studio: text to speech, transcription, subtitles, cloned voices."""

    def status(
        self,
        *,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """What this account may do in the AI Voice Studio, and what it has used.
        """
        return self._client._request(
            "GET",
            "/ai/status",
            timeout=timeout,
        )

    def pricing(
        self,
        *,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """The studio's plans, limits and prices.
        """
        return self._client._request(
            "GET",
            "/ai/pricing",
            timeout=timeout,
        )

    def builtin_voices(
        self,
        *,
        language: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """The built-in voices, optionally for one language.

        Args:
            language: Language code, e.g. en, hi (server default: 'en')
        """
        return self._client._request(
            "GET",
            "/ai/voices/builtin",
            query={"language": language},
            timeout=timeout,
        )

    def transcribe(
        self,
        file: FileInput,
        *,
        language: Optional[str] = None,
        diarize: Optional[bool] = None,
        translate: Optional[bool] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Turn an audio file into text.

        Args:
            file: The audio or video file
            language: Language code, e.g. en, hi
            diarize: Label who is speaking (server default: False)
            translate: Translate the transcript into English (server default: False)
        """
        return self._client._request(
            "POST",
            "/ai/transcribe",
            files={"file": file},
            form={"language": language, "diarize": diarize, "translate": translate},
            multipart=True,
            timeout=timeout,
        )

    def transcribe_video(
        self,
        file: FileInput,
        *,
        language: Optional[str] = None,
        diarize: Optional[bool] = None,
        translate: Optional[bool] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Turn the speech in a video file into text.

        Args:
            file: The audio or video file
            language: Language code, e.g. en, hi
            diarize: Label who is speaking (server default: False)
            translate: Translate the transcript into English (server default: False)
        """
        return self._client._request(
            "POST",
            "/ai/transcribe/video",
            files={"file": file},
            form={"language": language, "diarize": diarize, "translate": translate},
            multipart=True,
            timeout=timeout,
        )

    def subtitles(
        self,
        file: FileInput,
        *,
        language: Optional[str] = None,
        fmt: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> DipsacFile:
        """Make a subtitle file (SRT or VTT) from audio or video.

        Args:
            file: The audio or video file
            language: Language code, e.g. en, hi
            fmt: Output format (server default: 'srt')
        """
        return self._client._request(
            "POST",
            "/ai/subtitles",
            files={"file": file},
            form={"language": language, "fmt": fmt},
            multipart=True,
            timeout=timeout,
        )

    def speak(
        self,
        text: str,
        *,
        language: Optional[str] = None,
        voice: Optional[str] = None,
        cloned_voice: Optional[str] = None,
        speed: Optional[float] = None,
        style: Optional[str] = None,
        fmt: Optional[str] = None,
        background: Optional[bool] = None,
        timeout: Optional[float] = None,
    ) -> Union[DipsacFile, Job]:
        """Turn text into speech. With background=True it returns a Job to wait on, which is the way to synthesise long text.

        Args:
            text: The text to speak
            language: Language code, e.g. en, hi (server default: 'en')
            voice: A built-in voice, by name (see builtin_voices)
            cloned_voice: A cloned voice you registered, by name
            speed: Speaking rate; 1.0 is normal (server default: 1.0)
            style: Speaking style, where the voice supports one
            fmt: Output format (server default: 'wav')
            background: Return a Job at once and synthesise in the background (server
                default: False)

        Returns a Job instead of the result when the work is sent to the
        background; call its wait() for the result.
        """
        return self._client._request(
            "POST",
            "/ai/speak",
            form={"text": text, "language": language, "voice": voice, "cloned_voice": cloned_voice, "speed": speed, "style": style, "fmt": fmt, "async": background},
            timeout=timeout,
        )

    def job(
        self,
        job_id: str,
        *,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """The state of a background speech job, as the API reports it.
        """
        return self._client._request(
            "GET",
            f"/ai/jobs/{_seg(job_id)}",
            timeout=timeout,
        )

    def library(
        self,
        *,
        kind: Optional[str] = None,
        limit: Optional[int] = None,
        before_id: Optional[int] = None,
        search: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """List what this account has generated.

        Args:
            kind: Only this kind of generation
            limit: How many to return (server default: 30)
            before_id: Return items older than this id
            search: Only items whose text contains this
        """
        return self._client._request(
            "GET",
            "/ai/library",
            query={"kind": kind, "limit": limit, "before_id": before_id, "search": search},
            timeout=timeout,
        )

    def library_item(
        self,
        gen_id: int,
        *,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """One generation from the library, with its details.
        """
        return self._client._request(
            "GET",
            f"/ai/library/{_seg(gen_id)}",
            timeout=timeout,
        )

    def delete_library_item(
        self,
        gen_id: int,
        *,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Delete one generation from the library.
        """
        return self._client._request(
            "DELETE",
            f"/ai/library/{_seg(gen_id)}",
            timeout=timeout,
        )

    def library_audio(
        self,
        gen_id: int,
        *,
        format: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> DipsacFile:
        """Download the audio of one generation.

        Args:
            format: Download format, e.g. mp3
        """
        return self._client._request(
            "GET",
            f"/ai/library/{_seg(gen_id)}/audio",
            query={"format": format},
            timeout=timeout,
        )

    def voices(
        self,
        *,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """The cloned voices this account has registered.
        """
        return self._client._request(
            "GET",
            "/ai/voices",
            timeout=timeout,
        )

    def register_voice(
        self,
        name: str,
        file: FileInput,
        *,
        consent: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Register a cloned voice from a recording of the speaker.

        Args:
            name: A name for the voice
            file: The audio or video file
            consent: The speaker's consent statement
        """
        return self._client._request(
            "POST",
            "/ai/voices",
            files={"file": file},
            form={"name": name, "consent": consent},
            multipart=True,
            timeout=timeout,
        )

    def delete_voice(
        self,
        voice_id: int,
        *,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Erase a cloned voice.
        """
        return self._client._request(
            "DELETE",
            f"/ai/voices/{_seg(voice_id)}",
            timeout=timeout,
        )


class AsyncPdf(_AsyncResource):
    """PDF tools: merge, split, compress, convert, protect, watermark."""

    async def merge(
        self,
        files: Sequence[FileInput],
        *,
        page_filter: Optional[str] = None,
        pdf_filter: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> DipsacFile:
        """Merge several PDFs into one.

        Args:
            files: Two or more PDF files, merged in the order given
            page_filter: Pages to take from each file: all | odd | even (server default:
                'all')
            pdf_filter: Which files to include by position: all | odd | even (server
                default: 'all')
        """
        return await self._client._request(
            "POST",
            "/v1/pdf/merge",
            files={"files": files},
            form={"page_filter": page_filter, "pdf_filter": pdf_filter},
            multipart=True,
            timeout=timeout,
        )

    async def split(
        self,
        file: FileInput,
        pages: str,
        *,
        timeout: Optional[float] = None,
    ) -> DipsacFile:
        """Extract a page range into a new PDF.

        Args:
            file: The PDF to take pages from
            pages: 1-indexed selection, e.g. '1-3,5,9-'
        """
        return await self._client._request(
            "POST",
            "/v1/pdf/split",
            files={"file": file},
            form={"pages": pages},
            multipart=True,
            timeout=timeout,
        )

    async def delete_pages(
        self,
        file: FileInput,
        pages: str,
        *,
        timeout: Optional[float] = None,
    ) -> DipsacFile:
        """Remove pages from a PDF.

        Args:
            pages: 1-indexed selection to delete, e.g. '2,4-6'
        """
        return await self._client._request(
            "POST",
            "/v1/pdf/delete-pages",
            files={"file": file},
            form={"pages": pages},
            multipart=True,
            timeout=timeout,
        )

    async def rotate(
        self,
        file: FileInput,
        *,
        degrees: Optional[int] = None,
        pages: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> DipsacFile:
        """Rotate pages.

        Args:
            degrees: Clockwise rotation: 90, 180 or 270 (server default: 90)
            pages: Optional 1-indexed selection; blank rotates every page
        """
        return await self._client._request(
            "POST",
            "/v1/pdf/rotate",
            files={"file": file},
            form={"degrees": degrees, "pages": pages},
            multipart=True,
            timeout=timeout,
        )

    async def compress(
        self,
        file: FileInput,
        *,
        preset: Optional[str] = None,
        remove_metadata: Optional[bool] = None,
        mode: Optional[Literal['sync', 'async']] = None,
        timeout: Optional[float] = None,
    ) -> Union[DipsacFile, AsyncJob]:
        """Reduce PDF file size.

        Args:
            preset: screen | ebook | printer | prepress — smaller to larger (server default:
                'ebook')
            remove_metadata: Strip document metadata (server default: True)
            mode: 'async' returns a job id instead of the file (server default: 'sync')

        Returns a Job instead of the result when the work is sent to the
        background; call its wait() for the result.
        """
        return await self._client._request(
            "POST",
            "/v1/pdf/compress",
            files={"file": file},
            form={"preset": preset, "remove_metadata": remove_metadata, "mode": mode},
            multipart=True,
            timeout=timeout,
        )

    async def convert(
        self,
        file: FileInput,
        output_format: str,
        *,
        mode: Optional[Literal['sync', 'async']] = None,
        timeout: Optional[float] = None,
    ) -> Union[DipsacFile, AsyncJob]:
        """Convert a PDF to Word, Excel or PowerPoint.

        `xlsx` extracts detected tables — it is not a full-page conversion, and a PDF with
        no tables is an error rather than an empty workbook. `docx` needs a real text layer,
        so scanned pages will not convert.

        Args:
            output_format: docx | xlsx | pptx
            mode: 'async' returns a job id instead of the file (server default: 'sync')

        Returns a Job instead of the result when the work is sent to the
        background; call its wait() for the result.
        """
        return await self._client._request(
            "POST",
            "/v1/pdf/convert",
            files={"file": file},
            form={"output_format": output_format, "mode": mode},
            multipart=True,
            timeout=timeout,
        )

    async def from_office(
        self,
        file: FileInput,
        *,
        timeout: Optional[float] = None,
    ) -> DipsacFile:
        """Create a PDF from a Word or Excel file.

        Args:
            file: A .docx or .xlsx file
        """
        return await self._client._request(
            "POST",
            "/v1/pdf/from-office",
            files={"file": file},
            multipart=True,
            timeout=timeout,
        )

    async def protect(
        self,
        file: FileInput,
        password: str,
        *,
        owner_password: Optional[str] = None,
        allow_printing: Optional[bool] = None,
        allow_copying: Optional[bool] = None,
        timeout: Optional[float] = None,
    ) -> DipsacFile:
        """Password-protect a PDF.

        Args:
            password: Password needed to open the file
            owner_password: Password needed to change permissions; defaults to `password`
        """
        return await self._client._request(
            "POST",
            "/v1/pdf/protect",
            files={"file": file},
            form={"password": password, "owner_password": owner_password, "allow_printing": allow_printing, "allow_copying": allow_copying},
            multipart=True,
            timeout=timeout,
        )

    async def unlock(
        self,
        file: FileInput,
        *,
        password: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> DipsacFile:
        """Remove password protection.

        Args:
            password: The document's current open password
        """
        return await self._client._request(
            "POST",
            "/v1/pdf/unlock",
            files={"file": file},
            form={"password": password},
            multipart=True,
            timeout=timeout,
        )

    async def watermark(
        self,
        file: FileInput,
        *,
        text: Optional[str] = None,
        opacity: Optional[float] = None,
        font_size: Optional[int] = None,
        color: Optional[str] = None,
        position: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> DipsacFile:
        """Stamp a watermark across every page.

        Args:
            color: Hex colour, e.g. #FF0000 (server default: '#FF0000')
            position: diagonal | center | top | bottom (server default: 'diagonal')
        """
        return await self._client._request(
            "POST",
            "/v1/pdf/watermark",
            files={"file": file},
            form={"text": text, "opacity": opacity, "font_size": font_size, "color": color, "position": position},
            multipart=True,
            timeout=timeout,
        )

    async def metadata(
        self,
        file: FileInput,
        *,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Read a PDF's metadata.
        """
        return await self._client._request(
            "POST",
            "/v1/pdf/metadata",
            files={"file": file},
            multipart=True,
            timeout=timeout,
        )


class AsyncImage(_AsyncResource):
    """Image tools: convert, compress, resize, crop, remove a background."""

    async def convert(
        self,
        file: FileInput,
        output_format: str,
        *,
        quality: Optional[int] = None,
        background: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> DipsacFile:
        """Convert an image to another format.

        Args:
            file: Any supported image; the input format is detected
            output_format: png | jpg | webp | bmp | tiff | gif | avif | heic
            quality: Ignored by lossless formats (server default: 85)
            background: Fill for transparency when the target has no alpha channel (server
                default: '#FFFFFF')
        """
        return await self._client._request(
            "POST",
            "/v1/image/convert",
            files={"file": file},
            form={"output_format": output_format, "quality": quality, "background": background},
            multipart=True,
            timeout=timeout,
        )

    async def compress(
        self,
        file: FileInput,
        *,
        quality: Optional[int] = None,
        timeout: Optional[float] = None,
    ) -> DipsacFile:
        """Re-encode an image at a lower quality.

        Keeps the input format. A PNG is re-encoded losslessly with optimisation, so
        `quality` has no effect on it — use `/v1/image/convert` to WebP or AVIF if you want
        a real size drop on a PNG.
        """
        return await self._client._request(
            "POST",
            "/v1/image/compress",
            files={"file": file},
            form={"quality": quality},
            multipart=True,
            timeout=timeout,
        )

    async def resize(
        self,
        file: FileInput,
        *,
        width: Optional[int] = None,
        height: Optional[int] = None,
        fit: Optional[str] = None,
        quality: Optional[int] = None,
        timeout: Optional[float] = None,
    ) -> DipsacFile:
        """Resize an image.

        Args:
            width: 0 means derive from height (server default: 0)
            height: 0 means derive from width (server default: 0)
            fit: contain (keep aspect, fit inside) | cover (crop to fill) | exact (stretch)
                (server default: 'contain')
        """
        return await self._client._request(
            "POST",
            "/v1/image/resize",
            files={"file": file},
            form={"width": width, "height": height, "fit": fit, "quality": quality},
            multipart=True,
            timeout=timeout,
        )

    async def crop(
        self,
        file: FileInput,
        x: int,
        y: int,
        width: int,
        height: int,
        *,
        quality: Optional[int] = None,
        timeout: Optional[float] = None,
    ) -> DipsacFile:
        """Crop a rectangle out of an image.

        Args:
            x: Left edge in pixels
            y: Top edge in pixels
        """
        return await self._client._request(
            "POST",
            "/v1/image/crop",
            files={"file": file},
            form={"x": x, "y": y, "width": width, "height": height, "quality": quality},
            multipart=True,
            timeout=timeout,
        )

    async def remove_background(
        self,
        file: FileInput,
        *,
        output_format: Optional[str] = None,
        background: Optional[str] = None,
        mode: Optional[Literal['sync', 'async']] = None,
        timeout: Optional[float] = None,
    ) -> Union[DipsacFile, AsyncJob]:
        """Cut the subject out of a photo.

        Runs a segmentation model, so it is markedly slower than the other image endpoints —
        seconds, not milliseconds. Use `mode=async` in bulk.

        Args:
            output_format: png keeps transparency; jpg flattens onto `background` (server
                default: 'png')
            mode: 'async' returns a job id instead of the file (server default: 'sync')

        Returns a Job instead of the result when the work is sent to the
        background; call its wait() for the result.
        """
        return await self._client._request(
            "POST",
            "/v1/image/remove-background",
            files={"file": file},
            form={"output_format": output_format, "background": background, "mode": mode},
            multipart=True,
            timeout=timeout,
        )

    async def to_pdf(
        self,
        files: Sequence[FileInput],
        *,
        timeout: Optional[float] = None,
    ) -> DipsacFile:
        """Combine images into a single PDF.

        Args:
            files: One or more images, one page each, in order
        """
        return await self._client._request(
            "POST",
            "/v1/image/to-pdf",
            files={"files": files},
            multipart=True,
            timeout=timeout,
        )

    async def info(
        self,
        file: FileInput,
        *,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Read an image's dimensions and format.
        """
        return await self._client._request(
            "POST",
            "/v1/image/info",
            files={"file": file},
            multipart=True,
            timeout=timeout,
        )


class AsyncAudio(_AsyncResource):
    """Audio tools: convert, normalise loudness, join files. Needs the Pro plan."""

    async def convert(
        self,
        file: FileInput,
        output_format: str,
        *,
        mode: Optional[Literal['sync', 'async']] = None,
        timeout: Optional[float] = None,
    ) -> Union[DipsacFile, AsyncJob]:
        """Convert audio to another format.

        `amr` is narrowband by definition — the result is 8 kHz mono whatever went in.
        Everything else keeps the source sample rate and channels.

        Args:
            file: Any supported audio file
            output_format: mp3 | wav | ogg | aac | m4a | flac | amr

        Returns a Job instead of the result when the work is sent to the
        background; call its wait() for the result.
        """
        return await self._client._request(
            "POST",
            "/v1/audio/convert",
            files={"file": file},
            form={"output_format": output_format, "mode": mode},
            multipart=True,
            timeout=timeout,
        )

    async def normalize(
        self,
        file: FileInput,
        *,
        target_lufs: Optional[float] = None,
        mode: Optional[Literal['sync', 'async']] = None,
        timeout: Optional[float] = None,
    ) -> Union[DipsacFile, AsyncJob]:
        """Even out audio loudness.

        Args:
            target_lufs: Integrated loudness target; -14 LUFS matches most streaming
                platforms (server default: -14.0)

        Returns a Job instead of the result when the work is sent to the
        background; call its wait() for the result.
        """
        return await self._client._request(
            "POST",
            "/v1/audio/normalize",
            files={"file": file},
            form={"target_lufs": target_lufs, "mode": mode},
            multipart=True,
            timeout=timeout,
        )

    async def merge(
        self,
        files: Sequence[FileInput],
        *,
        timeout: Optional[float] = None,
    ) -> DipsacFile:
        """Join several audio files end to end.

        Args:
            files: Two or more audio files, joined in the order given
        """
        return await self._client._request(
            "POST",
            "/v1/audio/merge",
            files={"files": files},
            multipart=True,
            timeout=timeout,
        )


class AsyncVideo(_AsyncResource):
    """Video tools: convert, trim, resize, mute, pull the audio out. Needs the Pro plan."""

    async def convert(
        self,
        file: FileInput,
        output_format: str,
        *,
        mode: Optional[Literal['sync', 'async']] = None,
        timeout: Optional[float] = None,
    ) -> Union[DipsacFile, AsyncJob]:
        """Convert video to another container/codec.

        `webm` re-encodes with VP9, which is markedly slower than the H.264 targets. Use
        `mode=async` for anything longer than a short clip.

        Args:
            output_format: mp4 | avi | mkv | mov | webm

        Returns a Job instead of the result when the work is sent to the
        background; call its wait() for the result.
        """
        return await self._client._request(
            "POST",
            "/v1/video/convert",
            files={"file": file},
            form={"output_format": output_format, "mode": mode},
            multipart=True,
            timeout=timeout,
        )

    async def extract_audio(
        self,
        file: FileInput,
        *,
        output_format: Optional[str] = None,
        mode: Optional[Literal['sync', 'async']] = None,
        timeout: Optional[float] = None,
    ) -> Union[DipsacFile, AsyncJob]:
        """Pull the audio track out of a video.

        Args:
            output_format: mp3 | wav | ogg | aac | m4a | flac (server default: 'mp3')

        Returns a Job instead of the result when the work is sent to the
        background; call its wait() for the result.
        """
        return await self._client._request(
            "POST",
            "/v1/video/extract-audio",
            files={"file": file},
            form={"output_format": output_format, "mode": mode},
            multipart=True,
            timeout=timeout,
        )

    async def cut(
        self,
        file: FileInput,
        end: str,
        *,
        start: Optional[str] = None,
        mode: Optional[Literal['sync', 'async']] = None,
        timeout: Optional[float] = None,
    ) -> Union[DipsacFile, AsyncJob]:
        """Trim a video to a time range.

        Args:
            end: Seconds or timestamp; must be after start
            start: Seconds (12.5) or timestamp (00:01:30) (server default: '0')

        Returns a Job instead of the result when the work is sent to the
        background; call its wait() for the result.
        """
        return await self._client._request(
            "POST",
            "/v1/video/cut",
            files={"file": file},
            form={"start": start, "end": end, "mode": mode},
            multipart=True,
            timeout=timeout,
        )

    async def resize(
        self,
        file: FileInput,
        *,
        width: Optional[int] = None,
        height: Optional[int] = None,
        mode: Optional[Literal['sync', 'async']] = None,
        timeout: Optional[float] = None,
    ) -> Union[DipsacFile, AsyncJob]:
        """Scale a video to a new width/height.

        Args:
            width: 0 derives from height, keeping aspect (server default: 0)
            height: 0 derives from width, keeping aspect (server default: 0)

        Returns a Job instead of the result when the work is sent to the
        background; call its wait() for the result.
        """
        return await self._client._request(
            "POST",
            "/v1/video/resize",
            files={"file": file},
            form={"width": width, "height": height, "mode": mode},
            multipart=True,
            timeout=timeout,
        )

    async def mute(
        self,
        file: FileInput,
        *,
        mode: Optional[Literal['sync', 'async']] = None,
        timeout: Optional[float] = None,
    ) -> Union[DipsacFile, AsyncJob]:
        """Strip the audio track from a video.

        Returns a Job instead of the result when the work is sent to the
        background; call its wait() for the result.
        """
        return await self._client._request(
            "POST",
            "/v1/video/mute",
            files={"file": file},
            form={"mode": mode},
            multipart=True,
            timeout=timeout,
        )


class AsyncSeo(_AsyncResource):
    """SEO checks: meta tags, TLS certificate, redirects, WHOIS, canonical."""

    async def meta(
        self,
        title: str,
        description: str,
        url: str,
        *,
        image: Optional[str] = None,
        site_name: Optional[str] = None,
        keywords: Optional[str] = None,
        author: Optional[str] = None,
        twitter_card: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Generate meta and Open Graph tags.

        Produces the `<meta>`, Open Graph and Twitter Card block for a page.

        Args:
            url: Canonical URL of the page
            image: Absolute URL of the social preview image
            twitter_card: summary | summary_large_image | app | player (server default:
                'summary_large_image')
        """
        return await self._client._request(
            "POST",
            "/v1/seo/meta",
            json={"title": title, "description": description, "url": url, "image": image, "site_name": site_name, "keywords": keywords, "author": author, "twitter_card": twitter_card},
            timeout=timeout,
        )

    async def ssl(
        self,
        url: str,
        *,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Inspect a site's TLS certificate.

        Args:
            url: Domain or URL, e.g. example.com
        """
        return await self._client._request(
            "GET",
            "/v1/seo/ssl",
            query={"url": url},
            timeout=timeout,
        )

    async def redirects(
        self,
        url: str,
        *,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Follow a URL's redirect chain.

        Args:
            url: The starting URL
        """
        return await self._client._request(
            "GET",
            "/v1/seo/redirects",
            query={"url": url},
            timeout=timeout,
        )

    async def whois(
        self,
        url: str,
        *,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """WHOIS registration record for a domain.

        Args:
            url: Domain or URL
        """
        return await self._client._request(
            "GET",
            "/v1/seo/whois",
            query={"url": url},
            timeout=timeout,
        )

    async def domain_age(
        self,
        url: str,
        *,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """How long a domain has been registered.

        A projection of the WHOIS record — the registration and expiry dates and the age
        derived from them, without the rest of the record.

        Args:
            url: Domain or URL
        """
        return await self._client._request(
            "GET",
            "/v1/seo/domain-age",
            query={"url": url},
            timeout=timeout,
        )

    async def canonical(
        self,
        url: str,
        *,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Check a page's canonical URL.

        Args:
            url: The page to inspect
        """
        return await self._client._request(
            "GET",
            "/v1/seo/canonical",
            query={"url": url},
            timeout=timeout,
        )


class AsyncDev(_AsyncResource):
    """Developer utilities: bcrypt hashing, JSON validation and formatting."""

    async def hash(
        self,
        password: str,
        *,
        rounds: Optional[int] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Hash a password with bcrypt.

        The cost is the whole point of bcrypt, so it is a parameter rather than a constant.
        Note that it is exponential: `rounds=16` is 16x the CPU of `rounds=12` and takes a
        noticeable fraction of a second.

        Args:
            password: The plaintext to hash
            rounds: bcrypt cost. Each step doubles the work; 12 is Laravel's default (server
                default: 12)
        """
        return await self._client._request(
            "POST",
            "/v1/dev/hash",
            json={"password": password, "rounds": rounds},
            timeout=timeout,
        )

    async def hash_verify(
        self,
        password: str,
        hash: str,
        *,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Check a password against a bcrypt hash.

        A malformed hash is `matches: false`, not an error — telling the caller which of the
        two inputs was wrong is exactly what an attacker wants.

        Args:
            hash: A bcrypt hash to check against
        """
        return await self._client._request(
            "POST",
            "/v1/dev/hash/verify",
            json={"password": password, "hash": hash},
            timeout=timeout,
        )

    async def json(
        self,
        content: str,
        *,
        action: Optional[str] = None,
        indent: Optional[int] = None,
        sort_keys: Optional[bool] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Validate, format or minify JSON.

        A syntax error comes back as `valid: false` with the line and column, and HTTP 200 —
        the request itself was well-formed, and "this document is invalid" is the answer,
        not a failure to answer.

        Args:
            content: The JSON document, as text
            action: format | minify | validate (server default: 'format')
            indent: Spaces per level when action=format (server default: 2)
            sort_keys: Order object keys alphabetically (server default: False)
        """
        return await self._client._request(
            "POST",
            "/v1/dev/json",
            json={"content": content, "action": action, "indent": indent, "sort_keys": sort_keys},
            timeout=timeout,
        )


class AsyncGlb(_AsyncResource):
    """3D model (.glb) inspection and editing plans. Needs the Enterprise plan."""

    async def limits(
        self,
        *,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Every limit of the GLB routes.

        The numbers the three routes below hold a request to: the largest scene description,
        how many operations one edit may carry, how many images and of what size, how long
        one request may run. Read it once and check before you send; the numbers can change
        without a new version of this API.
        """
        return await self._client._request(
            "GET",
            "/v1/glb/limits",
            timeout=timeout,
        )

    async def inspect(
        self,
        head: FileInput,
        size: int,
        *,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """What a .glb is, and what may be done to it.

        Send the model's **head** and its size; the model itself is never sent.

        Args:
            head: The first bytes of the .glb, as a file part: its 12-byte header, its JSON
                chunk, and the 8-byte header of the chunk after it. That is `file.slice(0, 20 +
                jsonLength + 8)`, where jsonLength is the little-endian uint32 at byte 12. Never
                the whole file
            size: The length of the whole .glb in bytes
        """
        return await self._client._request(
            "POST",
            "/v1/glb/inspect",
            files={"head": head},
            form={"size": size},
            multipart=True,
            timeout=timeout,
        )

    async def plan(
        self,
        head: FileInput,
        size: int,
        edit: str,
        *,
        images: Optional[Sequence[FileInput]] = None,
        hashes: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Compile edits to a .glb into a plan of byte ranges.

        Answers `{"segments": [...], "total": N, "report": {...}}`. **You build the edited
        file** by concatenating the segments in order:

        Args:
            head: The first bytes of the .glb, as a file part: its 12-byte header, its JSON
                chunk, and the 8-byte header of the chunk after it. That is `file.slice(0, 20 +
                jsonLength + 8)`, where jsonLength is the little-endian uint32 at byte 12. Never
                the whole file
            size: The length of the whole .glb in bytes
            edit: JSON: `{"ops": [...], "cleanup": {...}, "removal": "required" | "unlink",
                "mode": "plan" | "check"}`. An operation names things by their index in the file
                as it arrived
            images: PNG or JPEG file parts an operation puts into the model. Each part's
                FILENAME is the name an operation refers to it by
            hashes: JSON `{"<image index>": "<sha-256, 64 lowercase hex>"}`, each computed
                by the caller over the image's own bytes. Needed only when `cleanup.dedupe` is
                asked for
        """
        return await self._client._request(
            "POST",
            "/v1/glb/plan",
            files={"head": head, "images": images},
            form={"size": size, "edit": edit, "hashes": hashes},
            multipart=True,
            timeout=timeout,
        )

    async def image(
        self,
        image: FileInput,
        *,
        max_size: Optional[int] = None,
        jpeg_quality: Optional[int] = None,
        to_jpeg: Optional[bool] = None,
        timeout: Optional[float] = None,
    ) -> Any:
        """Shrink one texture.

        A smaller picture comes back as bytes (`image/png` or `image/jpeg`) with `X-Glb-*`
        headers saying what was done. A picture that was left alone comes back as JSON,
        `{"changed": false, "outcome": "..."}`, with one word saying why. The ranges
        `max_size` and `jpeg_quality` may take are in `GET /v1/glb/limits`.

        Args:
            image: One PNG or JPEG
            max_size: The longest side, in pixels, of the picture that comes back
            jpeg_quality: The quality a JPEG is written at
            to_jpeg: Allow a PNG with no transparency to come back as a JPEG. Only where
                inspect says `jpeg_allowed` for that image
        """
        return await self._client._request(
            "POST",
            "/v1/glb/image",
            files={"image": image},
            form={"max_size": max_size, "jpeg_quality": jpeg_quality, "to_jpeg": to_jpeg},
            multipart=True,
            timeout=timeout,
        )


class AsyncJobs(_AsyncResource):
    """Status and result of work submitted with mode="async"."""

    async def get(
        self,
        job_id: str,
        *,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Check the status of an async job.

        Poll this until `status` is `succeeded` or `failed`. A second or two between polls
        is plenty; the work is measured in seconds, not milliseconds.
        """
        return await self._client._request(
            "GET",
            f"/v1/jobs/{_seg(job_id)}",
            timeout=timeout,
        )

    async def result(
        self,
        job_id: str,
        *,
        timeout: Optional[float] = None,
    ) -> DipsacFile:
        """Download a finished job's output.
        """
        return await self._client._request(
            "GET",
            f"/v1/jobs/{_seg(job_id)}/result",
            timeout=timeout,
        )


class AsyncAi(_AsyncResource):
    """AI Voice Studio: text to speech, transcription, subtitles, cloned voices."""

    async def status(
        self,
        *,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """What this account may do in the AI Voice Studio, and what it has used.
        """
        return await self._client._request(
            "GET",
            "/ai/status",
            timeout=timeout,
        )

    async def pricing(
        self,
        *,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """The studio's plans, limits and prices.
        """
        return await self._client._request(
            "GET",
            "/ai/pricing",
            timeout=timeout,
        )

    async def builtin_voices(
        self,
        *,
        language: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """The built-in voices, optionally for one language.

        Args:
            language: Language code, e.g. en, hi (server default: 'en')
        """
        return await self._client._request(
            "GET",
            "/ai/voices/builtin",
            query={"language": language},
            timeout=timeout,
        )

    async def transcribe(
        self,
        file: FileInput,
        *,
        language: Optional[str] = None,
        diarize: Optional[bool] = None,
        translate: Optional[bool] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Turn an audio file into text.

        Args:
            file: The audio or video file
            language: Language code, e.g. en, hi
            diarize: Label who is speaking (server default: False)
            translate: Translate the transcript into English (server default: False)
        """
        return await self._client._request(
            "POST",
            "/ai/transcribe",
            files={"file": file},
            form={"language": language, "diarize": diarize, "translate": translate},
            multipart=True,
            timeout=timeout,
        )

    async def transcribe_video(
        self,
        file: FileInput,
        *,
        language: Optional[str] = None,
        diarize: Optional[bool] = None,
        translate: Optional[bool] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Turn the speech in a video file into text.

        Args:
            file: The audio or video file
            language: Language code, e.g. en, hi
            diarize: Label who is speaking (server default: False)
            translate: Translate the transcript into English (server default: False)
        """
        return await self._client._request(
            "POST",
            "/ai/transcribe/video",
            files={"file": file},
            form={"language": language, "diarize": diarize, "translate": translate},
            multipart=True,
            timeout=timeout,
        )

    async def subtitles(
        self,
        file: FileInput,
        *,
        language: Optional[str] = None,
        fmt: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> DipsacFile:
        """Make a subtitle file (SRT or VTT) from audio or video.

        Args:
            file: The audio or video file
            language: Language code, e.g. en, hi
            fmt: Output format (server default: 'srt')
        """
        return await self._client._request(
            "POST",
            "/ai/subtitles",
            files={"file": file},
            form={"language": language, "fmt": fmt},
            multipart=True,
            timeout=timeout,
        )

    async def speak(
        self,
        text: str,
        *,
        language: Optional[str] = None,
        voice: Optional[str] = None,
        cloned_voice: Optional[str] = None,
        speed: Optional[float] = None,
        style: Optional[str] = None,
        fmt: Optional[str] = None,
        background: Optional[bool] = None,
        timeout: Optional[float] = None,
    ) -> Union[DipsacFile, AsyncJob]:
        """Turn text into speech. With background=True it returns a Job to wait on, which is the way to synthesise long text.

        Args:
            text: The text to speak
            language: Language code, e.g. en, hi (server default: 'en')
            voice: A built-in voice, by name (see builtin_voices)
            cloned_voice: A cloned voice you registered, by name
            speed: Speaking rate; 1.0 is normal (server default: 1.0)
            style: Speaking style, where the voice supports one
            fmt: Output format (server default: 'wav')
            background: Return a Job at once and synthesise in the background (server
                default: False)

        Returns a Job instead of the result when the work is sent to the
        background; call its wait() for the result.
        """
        return await self._client._request(
            "POST",
            "/ai/speak",
            form={"text": text, "language": language, "voice": voice, "cloned_voice": cloned_voice, "speed": speed, "style": style, "fmt": fmt, "async": background},
            timeout=timeout,
        )

    async def job(
        self,
        job_id: str,
        *,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """The state of a background speech job, as the API reports it.
        """
        return await self._client._request(
            "GET",
            f"/ai/jobs/{_seg(job_id)}",
            timeout=timeout,
        )

    async def library(
        self,
        *,
        kind: Optional[str] = None,
        limit: Optional[int] = None,
        before_id: Optional[int] = None,
        search: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """List what this account has generated.

        Args:
            kind: Only this kind of generation
            limit: How many to return (server default: 30)
            before_id: Return items older than this id
            search: Only items whose text contains this
        """
        return await self._client._request(
            "GET",
            "/ai/library",
            query={"kind": kind, "limit": limit, "before_id": before_id, "search": search},
            timeout=timeout,
        )

    async def library_item(
        self,
        gen_id: int,
        *,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """One generation from the library, with its details.
        """
        return await self._client._request(
            "GET",
            f"/ai/library/{_seg(gen_id)}",
            timeout=timeout,
        )

    async def delete_library_item(
        self,
        gen_id: int,
        *,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Delete one generation from the library.
        """
        return await self._client._request(
            "DELETE",
            f"/ai/library/{_seg(gen_id)}",
            timeout=timeout,
        )

    async def library_audio(
        self,
        gen_id: int,
        *,
        format: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> DipsacFile:
        """Download the audio of one generation.

        Args:
            format: Download format, e.g. mp3
        """
        return await self._client._request(
            "GET",
            f"/ai/library/{_seg(gen_id)}/audio",
            query={"format": format},
            timeout=timeout,
        )

    async def voices(
        self,
        *,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """The cloned voices this account has registered.
        """
        return await self._client._request(
            "GET",
            "/ai/voices",
            timeout=timeout,
        )

    async def register_voice(
        self,
        name: str,
        file: FileInput,
        *,
        consent: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Register a cloned voice from a recording of the speaker.

        Args:
            name: A name for the voice
            file: The audio or video file
            consent: The speaker's consent statement
        """
        return await self._client._request(
            "POST",
            "/ai/voices",
            files={"file": file},
            form={"name": name, "consent": consent},
            multipart=True,
            timeout=timeout,
        )

    async def delete_voice(
        self,
        voice_id: int,
        *,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Erase a cloned voice.
        """
        return await self._client._request(
            "DELETE",
            f"/ai/voices/{_seg(voice_id)}",
            timeout=timeout,
        )


RESOURCES = {
    "pdf": (Pdf, AsyncPdf),
    "image": (Image, AsyncImage),
    "audio": (Audio, AsyncAudio),
    "video": (Video, AsyncVideo),
    "seo": (Seo, AsyncSeo),
    "dev": (Dev, AsyncDev),
    "glb": (Glb, AsyncGlb),
    "jobs": (Jobs, AsyncJobs),
    "ai": (Ai, AsyncAi),
}


OPERATIONS = (
    ("POST", "/v1/pdf/merge", "pdf", "merge"),
    ("POST", "/v1/pdf/split", "pdf", "split"),
    ("POST", "/v1/pdf/delete-pages", "pdf", "delete_pages"),
    ("POST", "/v1/pdf/rotate", "pdf", "rotate"),
    ("POST", "/v1/pdf/compress", "pdf", "compress"),
    ("POST", "/v1/pdf/convert", "pdf", "convert"),
    ("POST", "/v1/pdf/from-office", "pdf", "from_office"),
    ("POST", "/v1/pdf/protect", "pdf", "protect"),
    ("POST", "/v1/pdf/unlock", "pdf", "unlock"),
    ("POST", "/v1/pdf/watermark", "pdf", "watermark"),
    ("POST", "/v1/pdf/metadata", "pdf", "metadata"),
    ("POST", "/v1/image/convert", "image", "convert"),
    ("POST", "/v1/image/compress", "image", "compress"),
    ("POST", "/v1/image/resize", "image", "resize"),
    ("POST", "/v1/image/crop", "image", "crop"),
    ("POST", "/v1/image/remove-background", "image", "remove_background"),
    ("POST", "/v1/image/to-pdf", "image", "to_pdf"),
    ("POST", "/v1/image/info", "image", "info"),
    ("POST", "/v1/audio/convert", "audio", "convert"),
    ("POST", "/v1/audio/normalize", "audio", "normalize"),
    ("POST", "/v1/audio/merge", "audio", "merge"),
    ("POST", "/v1/video/convert", "video", "convert"),
    ("POST", "/v1/video/extract-audio", "video", "extract_audio"),
    ("POST", "/v1/video/cut", "video", "cut"),
    ("POST", "/v1/video/resize", "video", "resize"),
    ("POST", "/v1/video/mute", "video", "mute"),
    ("POST", "/v1/seo/meta", "seo", "meta"),
    ("GET", "/v1/seo/ssl", "seo", "ssl"),
    ("GET", "/v1/seo/redirects", "seo", "redirects"),
    ("GET", "/v1/seo/whois", "seo", "whois"),
    ("GET", "/v1/seo/domain-age", "seo", "domain_age"),
    ("GET", "/v1/seo/canonical", "seo", "canonical"),
    ("POST", "/v1/dev/hash", "dev", "hash"),
    ("POST", "/v1/dev/hash/verify", "dev", "hash_verify"),
    ("POST", "/v1/dev/json", "dev", "json"),
    ("GET", "/v1/glb/limits", "glb", "limits"),
    ("POST", "/v1/glb/inspect", "glb", "inspect"),
    ("POST", "/v1/glb/plan", "glb", "plan"),
    ("POST", "/v1/glb/image", "glb", "image"),
    ("GET", "/v1/jobs/{job_id}", "jobs", "get"),
    ("GET", "/v1/jobs/{job_id}/result", "jobs", "result"),
    ("GET", "/ai/status", "ai", "status"),
    ("GET", "/ai/pricing", "ai", "pricing"),
    ("GET", "/ai/voices/builtin", "ai", "builtin_voices"),
    ("POST", "/ai/transcribe", "ai", "transcribe"),
    ("POST", "/ai/transcribe/video", "ai", "transcribe_video"),
    ("POST", "/ai/subtitles", "ai", "subtitles"),
    ("POST", "/ai/speak", "ai", "speak"),
    ("GET", "/ai/jobs/{job_id}", "ai", "job"),
    ("GET", "/ai/library", "ai", "library"),
    ("GET", "/ai/library/{gen_id}", "ai", "library_item"),
    ("DELETE", "/ai/library/{gen_id}", "ai", "delete_library_item"),
    ("GET", "/ai/library/{gen_id}/audio", "ai", "library_audio"),
    ("GET", "/ai/voices", "ai", "voices"),
    ("POST", "/ai/voices", "ai", "register_voice"),
    ("DELETE", "/ai/voices/{voice_id}", "ai", "delete_voice"),
)
