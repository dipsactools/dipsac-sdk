// The API's operations, one method each. GENERATED: do not edit.
//
// Written by codegen/generate.py from openapi/dipsac.openapi.json. To change a
// method, change the schema snapshot (or the tables in the generator) and run
// it again.
import type { Dipsac, RequestOptions } from "./client.js";
import type { FileInput } from "./files.js";
import type { DipsacFile, Job, JsonObject } from "./models.js";

const seg = (value: string | number): string => encodeURIComponent(String(value));

class Resource {
  constructor(protected readonly client: Dipsac) {}
}

export interface PdfMergeParams {
  /** Two or more PDF files, merged in the order given */
  files: FileInput[];
  /** Pages to take from each file: all | odd | even (server default: 'all') */
  pageFilter?: string;
  /** Which files to include by position: all | odd | even (server default: 'all') */
  pdfFilter?: string;
}

export interface PdfSplitParams {
  /** The PDF to take pages from */
  file: FileInput;
  /** 1-indexed selection, e.g. '1-3,5,9-' */
  pages: string;
}

export interface PdfDeletePagesParams {
  file: FileInput;
  /** 1-indexed selection to delete, e.g. '2,4-6' */
  pages: string;
}

export interface PdfRotateParams {
  file: FileInput;
  /** Clockwise rotation: 90, 180 or 270 (server default: 90) */
  degrees?: number;
  /** Optional 1-indexed selection; blank rotates every page */
  pages?: string;
}

export interface PdfCompressParams {
  file: FileInput;
  /** screen | ebook | printer | prepress — smaller to larger (server default: 'ebook') */
  preset?: string;
  /** Strip document metadata (server default: True) */
  removeMetadata?: boolean;
  /** 'async' returns a job id instead of the file (server default: 'sync') */
  mode?: "sync" | "async";
}

export interface PdfConvertParams {
  file: FileInput;
  /** docx | xlsx | pptx */
  outputFormat: string;
  /** 'async' returns a job id instead of the file (server default: 'sync') */
  mode?: "sync" | "async";
}

export interface PdfFromOfficeParams {
  /** A .docx or .xlsx file */
  file: FileInput;
}

export interface PdfProtectParams {
  file: FileInput;
  /** Password needed to open the file */
  password: string;
  /** Password needed to change permissions; defaults to `password` */
  ownerPassword?: string;
  allowPrinting?: boolean;
  allowCopying?: boolean;
}

export interface PdfUnlockParams {
  file: FileInput;
  /** The document's current open password */
  password?: string;
}

export interface PdfWatermarkParams {
  file: FileInput;
  text?: string;
  opacity?: number;
  fontSize?: number;
  /** Hex colour, e.g. #FF0000 (server default: '#FF0000') */
  color?: string;
  /** diagonal | center | top | bottom (server default: 'diagonal') */
  position?: string;
}

export interface PdfMetadataParams {
  file: FileInput;
}

/** PDF tools: merge, split, compress, convert, protect, watermark. */
export class Pdf extends Resource {
  /**
   * Merge several PDFs into one.
   */
  merge(params: PdfMergeParams, options?: RequestOptions): Promise<DipsacFile> {
    return this.client.request({ method: "POST", path: "/v1/pdf/merge", files: { files: params.files }, form: { page_filter: params.pageFilter, pdf_filter: params.pdfFilter }, multipart: true }, options) as Promise<DipsacFile>;
  }

  /**
   * Extract a page range into a new PDF.
   */
  split(params: PdfSplitParams, options?: RequestOptions): Promise<DipsacFile> {
    return this.client.request({ method: "POST", path: "/v1/pdf/split", files: { file: params.file }, form: { pages: params.pages }, multipart: true }, options) as Promise<DipsacFile>;
  }

  /**
   * Remove pages from a PDF.
   */
  deletePages(params: PdfDeletePagesParams, options?: RequestOptions): Promise<DipsacFile> {
    return this.client.request({ method: "POST", path: "/v1/pdf/delete-pages", files: { file: params.file }, form: { pages: params.pages }, multipart: true }, options) as Promise<DipsacFile>;
  }

  /**
   * Rotate pages.
   */
  rotate(params: PdfRotateParams, options?: RequestOptions): Promise<DipsacFile> {
    return this.client.request({ method: "POST", path: "/v1/pdf/rotate", files: { file: params.file }, form: { degrees: params.degrees, pages: params.pages }, multipart: true }, options) as Promise<DipsacFile>;
  }

  /**
   * Reduce PDF file size.
   *
   * Resolves to a Job instead of the result when the work is sent to the
   * background; await its wait() for the result.
   */
  compress(params: PdfCompressParams, options?: RequestOptions): Promise<DipsacFile | Job> {
    return this.client.request({ method: "POST", path: "/v1/pdf/compress", files: { file: params.file }, form: { preset: params.preset, remove_metadata: params.removeMetadata, mode: params.mode }, multipart: true }, options) as Promise<DipsacFile | Job>;
  }

  /**
   * Convert a PDF to Word, Excel or PowerPoint.
   *
   * `xlsx` extracts detected tables — it is not a full-page conversion, and a PDF with
   * no tables is an error rather than an empty workbook. `docx` needs a real text layer,
   * so scanned pages will not convert.
   *
   * Resolves to a Job instead of the result when the work is sent to the
   * background; await its wait() for the result.
   */
  convert(params: PdfConvertParams, options?: RequestOptions): Promise<DipsacFile | Job> {
    return this.client.request({ method: "POST", path: "/v1/pdf/convert", files: { file: params.file }, form: { output_format: params.outputFormat, mode: params.mode }, multipart: true }, options) as Promise<DipsacFile | Job>;
  }

  /**
   * Create a PDF from a Word or Excel file.
   */
  fromOffice(params: PdfFromOfficeParams, options?: RequestOptions): Promise<DipsacFile> {
    return this.client.request({ method: "POST", path: "/v1/pdf/from-office", files: { file: params.file }, multipart: true }, options) as Promise<DipsacFile>;
  }

  /**
   * Password-protect a PDF.
   */
  protect(params: PdfProtectParams, options?: RequestOptions): Promise<DipsacFile> {
    return this.client.request({ method: "POST", path: "/v1/pdf/protect", files: { file: params.file }, form: { password: params.password, owner_password: params.ownerPassword, allow_printing: params.allowPrinting, allow_copying: params.allowCopying }, multipart: true }, options) as Promise<DipsacFile>;
  }

  /**
   * Remove password protection.
   */
  unlock(params: PdfUnlockParams, options?: RequestOptions): Promise<DipsacFile> {
    return this.client.request({ method: "POST", path: "/v1/pdf/unlock", files: { file: params.file }, form: { password: params.password }, multipart: true }, options) as Promise<DipsacFile>;
  }

  /**
   * Stamp a watermark across every page.
   */
  watermark(params: PdfWatermarkParams, options?: RequestOptions): Promise<DipsacFile> {
    return this.client.request({ method: "POST", path: "/v1/pdf/watermark", files: { file: params.file }, form: { text: params.text, opacity: params.opacity, font_size: params.fontSize, color: params.color, position: params.position }, multipart: true }, options) as Promise<DipsacFile>;
  }

  /**
   * Read a PDF's metadata.
   */
  metadata(params: PdfMetadataParams, options?: RequestOptions): Promise<JsonObject> {
    return this.client.request({ method: "POST", path: "/v1/pdf/metadata", files: { file: params.file }, multipart: true }, options) as Promise<JsonObject>;
  }
}

export interface ImageConvertParams {
  /** Any supported image; the input format is detected */
  file: FileInput;
  /** png | jpg | webp | bmp | tiff | gif | avif | heic */
  outputFormat: string;
  /** Ignored by lossless formats (server default: 85) */
  quality?: number;
  /** Fill for transparency when the target has no alpha channel (server default: '#FFFFFF') */
  background?: string;
}

export interface ImageCompressParams {
  file: FileInput;
  quality?: number;
}

export interface ImageResizeParams {
  file: FileInput;
  /** 0 means derive from height (server default: 0) */
  width?: number;
  /** 0 means derive from width (server default: 0) */
  height?: number;
  /** contain (keep aspect, fit inside) | cover (crop to fill) | exact (stretch) (server default: 'contain') */
  fit?: string;
  quality?: number;
}

export interface ImageCropParams {
  file: FileInput;
  /** Left edge in pixels */
  x: number;
  /** Top edge in pixels */
  y: number;
  width: number;
  height: number;
  quality?: number;
}

export interface ImageRemoveBackgroundParams {
  file: FileInput;
  /** png keeps transparency; jpg flattens onto `background` (server default: 'png') */
  outputFormat?: string;
  background?: string;
  /** 'async' returns a job id instead of the file (server default: 'sync') */
  mode?: "sync" | "async";
}

export interface ImageToPdfParams {
  /** One or more images, one page each, in order */
  files: FileInput[];
}

export interface ImageInfoParams {
  file: FileInput;
}

/** Image tools: convert, compress, resize, crop, remove a background. */
export class Image extends Resource {
  /**
   * Convert an image to another format.
   */
  convert(params: ImageConvertParams, options?: RequestOptions): Promise<DipsacFile> {
    return this.client.request({ method: "POST", path: "/v1/image/convert", files: { file: params.file }, form: { output_format: params.outputFormat, quality: params.quality, background: params.background }, multipart: true }, options) as Promise<DipsacFile>;
  }

  /**
   * Re-encode an image at a lower quality.
   *
   * Keeps the input format. A PNG is re-encoded losslessly with optimisation, so
   * `quality` has no effect on it — use `/v1/image/convert` to WebP or AVIF if you want
   * a real size drop on a PNG.
   */
  compress(params: ImageCompressParams, options?: RequestOptions): Promise<DipsacFile> {
    return this.client.request({ method: "POST", path: "/v1/image/compress", files: { file: params.file }, form: { quality: params.quality }, multipart: true }, options) as Promise<DipsacFile>;
  }

  /**
   * Resize an image.
   */
  resize(params: ImageResizeParams, options?: RequestOptions): Promise<DipsacFile> {
    return this.client.request({ method: "POST", path: "/v1/image/resize", files: { file: params.file }, form: { width: params.width, height: params.height, fit: params.fit, quality: params.quality }, multipart: true }, options) as Promise<DipsacFile>;
  }

  /**
   * Crop a rectangle out of an image.
   */
  crop(params: ImageCropParams, options?: RequestOptions): Promise<DipsacFile> {
    return this.client.request({ method: "POST", path: "/v1/image/crop", files: { file: params.file }, form: { x: params.x, y: params.y, width: params.width, height: params.height, quality: params.quality }, multipart: true }, options) as Promise<DipsacFile>;
  }

  /**
   * Cut the subject out of a photo.
   *
   * Runs a segmentation model, so it is markedly slower than the other image endpoints —
   * seconds, not milliseconds. Use `mode=async` in bulk.
   *
   * Resolves to a Job instead of the result when the work is sent to the
   * background; await its wait() for the result.
   */
  removeBackground(params: ImageRemoveBackgroundParams, options?: RequestOptions): Promise<DipsacFile | Job> {
    return this.client.request({ method: "POST", path: "/v1/image/remove-background", files: { file: params.file }, form: { output_format: params.outputFormat, background: params.background, mode: params.mode }, multipart: true }, options) as Promise<DipsacFile | Job>;
  }

  /**
   * Combine images into a single PDF.
   */
  toPdf(params: ImageToPdfParams, options?: RequestOptions): Promise<DipsacFile> {
    return this.client.request({ method: "POST", path: "/v1/image/to-pdf", files: { files: params.files }, multipart: true }, options) as Promise<DipsacFile>;
  }

  /**
   * Read an image's dimensions and format.
   */
  info(params: ImageInfoParams, options?: RequestOptions): Promise<JsonObject> {
    return this.client.request({ method: "POST", path: "/v1/image/info", files: { file: params.file }, multipart: true }, options) as Promise<JsonObject>;
  }
}

export interface AudioConvertParams {
  /** Any supported audio file */
  file: FileInput;
  /** mp3 | wav | ogg | aac | m4a | flac | amr */
  outputFormat: string;
  mode?: "sync" | "async";
}

export interface AudioNormalizeParams {
  file: FileInput;
  /** Integrated loudness target; -14 LUFS matches most streaming platforms (server default: -14.0) */
  targetLufs?: number;
  mode?: "sync" | "async";
}

export interface AudioMergeParams {
  /** Two or more audio files, joined in the order given */
  files: FileInput[];
}

/** Audio tools: convert, normalise loudness, join files. Needs the Pro plan. */
export class Audio extends Resource {
  /**
   * Convert audio to another format.
   *
   * `amr` is narrowband by definition — the result is 8 kHz mono whatever went in.
   * Everything else keeps the source sample rate and channels.
   *
   * Resolves to a Job instead of the result when the work is sent to the
   * background; await its wait() for the result.
   */
  convert(params: AudioConvertParams, options?: RequestOptions): Promise<DipsacFile | Job> {
    return this.client.request({ method: "POST", path: "/v1/audio/convert", files: { file: params.file }, form: { output_format: params.outputFormat, mode: params.mode }, multipart: true }, options) as Promise<DipsacFile | Job>;
  }

  /**
   * Even out audio loudness.
   *
   * Resolves to a Job instead of the result when the work is sent to the
   * background; await its wait() for the result.
   */
  normalize(params: AudioNormalizeParams, options?: RequestOptions): Promise<DipsacFile | Job> {
    return this.client.request({ method: "POST", path: "/v1/audio/normalize", files: { file: params.file }, form: { target_lufs: params.targetLufs, mode: params.mode }, multipart: true }, options) as Promise<DipsacFile | Job>;
  }

  /**
   * Join several audio files end to end.
   */
  merge(params: AudioMergeParams, options?: RequestOptions): Promise<DipsacFile> {
    return this.client.request({ method: "POST", path: "/v1/audio/merge", files: { files: params.files }, multipart: true }, options) as Promise<DipsacFile>;
  }
}

export interface VideoConvertParams {
  file: FileInput;
  /** mp4 | avi | mkv | mov | webm */
  outputFormat: string;
  mode?: "sync" | "async";
}

export interface VideoExtractAudioParams {
  file: FileInput;
  /** mp3 | wav | ogg | aac | m4a | flac (server default: 'mp3') */
  outputFormat?: string;
  mode?: "sync" | "async";
}

export interface VideoCutParams {
  file: FileInput;
  /** Seconds or timestamp; must be after start */
  end: string;
  /** Seconds (12.5) or timestamp (00:01:30) (server default: '0') */
  start?: string;
  mode?: "sync" | "async";
}

export interface VideoResizeParams {
  file: FileInput;
  /** 0 derives from height, keeping aspect (server default: 0) */
  width?: number;
  /** 0 derives from width, keeping aspect (server default: 0) */
  height?: number;
  mode?: "sync" | "async";
}

export interface VideoMuteParams {
  file: FileInput;
  mode?: "sync" | "async";
}

/** Video tools: convert, trim, resize, mute, pull the audio out. Needs the Pro plan. */
export class Video extends Resource {
  /**
   * Convert video to another container/codec.
   *
   * `webm` re-encodes with VP9, which is markedly slower than the H.264 targets. Use
   * `mode=async` for anything longer than a short clip.
   *
   * Resolves to a Job instead of the result when the work is sent to the
   * background; await its wait() for the result.
   */
  convert(params: VideoConvertParams, options?: RequestOptions): Promise<DipsacFile | Job> {
    return this.client.request({ method: "POST", path: "/v1/video/convert", files: { file: params.file }, form: { output_format: params.outputFormat, mode: params.mode }, multipart: true }, options) as Promise<DipsacFile | Job>;
  }

  /**
   * Pull the audio track out of a video.
   *
   * Resolves to a Job instead of the result when the work is sent to the
   * background; await its wait() for the result.
   */
  extractAudio(params: VideoExtractAudioParams, options?: RequestOptions): Promise<DipsacFile | Job> {
    return this.client.request({ method: "POST", path: "/v1/video/extract-audio", files: { file: params.file }, form: { output_format: params.outputFormat, mode: params.mode }, multipart: true }, options) as Promise<DipsacFile | Job>;
  }

  /**
   * Trim a video to a time range.
   *
   * Resolves to a Job instead of the result when the work is sent to the
   * background; await its wait() for the result.
   */
  cut(params: VideoCutParams, options?: RequestOptions): Promise<DipsacFile | Job> {
    return this.client.request({ method: "POST", path: "/v1/video/cut", files: { file: params.file }, form: { start: params.start, end: params.end, mode: params.mode }, multipart: true }, options) as Promise<DipsacFile | Job>;
  }

  /**
   * Scale a video to a new width/height.
   *
   * Resolves to a Job instead of the result when the work is sent to the
   * background; await its wait() for the result.
   */
  resize(params: VideoResizeParams, options?: RequestOptions): Promise<DipsacFile | Job> {
    return this.client.request({ method: "POST", path: "/v1/video/resize", files: { file: params.file }, form: { width: params.width, height: params.height, mode: params.mode }, multipart: true }, options) as Promise<DipsacFile | Job>;
  }

  /**
   * Strip the audio track from a video.
   *
   * Resolves to a Job instead of the result when the work is sent to the
   * background; await its wait() for the result.
   */
  mute(params: VideoMuteParams, options?: RequestOptions): Promise<DipsacFile | Job> {
    return this.client.request({ method: "POST", path: "/v1/video/mute", files: { file: params.file }, form: { mode: params.mode }, multipart: true }, options) as Promise<DipsacFile | Job>;
  }
}

export interface SeoMetaParams {
  title: string;
  description: string;
  /** Canonical URL of the page */
  url: string;
  /** Absolute URL of the social preview image */
  image?: string;
  siteName?: string;
  keywords?: string;
  author?: string;
  /** summary | summary_large_image | app | player (server default: 'summary_large_image') */
  twitterCard?: string;
}

export interface SeoSslParams {
  /** Domain or URL, e.g. example.com */
  url: string;
}

export interface SeoRedirectsParams {
  /** The starting URL */
  url: string;
}

export interface SeoWhoisParams {
  /** Domain or URL */
  url: string;
}

export interface SeoDomainAgeParams {
  /** Domain or URL */
  url: string;
}

export interface SeoCanonicalParams {
  /** The page to inspect */
  url: string;
}

/** SEO checks: meta tags, TLS certificate, redirects, WHOIS, canonical. */
export class Seo extends Resource {
  /**
   * Generate meta and Open Graph tags.
   *
   * Produces the `<meta>`, Open Graph and Twitter Card block for a page.
   */
  meta(params: SeoMetaParams, options?: RequestOptions): Promise<JsonObject> {
    return this.client.request({ method: "POST", path: "/v1/seo/meta", json: { title: params.title, description: params.description, url: params.url, image: params.image, site_name: params.siteName, keywords: params.keywords, author: params.author, twitter_card: params.twitterCard } }, options) as Promise<JsonObject>;
  }

  /**
   * Inspect a site's TLS certificate.
   */
  ssl(params: SeoSslParams, options?: RequestOptions): Promise<JsonObject> {
    return this.client.request({ method: "GET", path: "/v1/seo/ssl", query: { url: params.url } }, options) as Promise<JsonObject>;
  }

  /**
   * Follow a URL's redirect chain.
   */
  redirects(params: SeoRedirectsParams, options?: RequestOptions): Promise<JsonObject> {
    return this.client.request({ method: "GET", path: "/v1/seo/redirects", query: { url: params.url } }, options) as Promise<JsonObject>;
  }

  /**
   * WHOIS registration record for a domain.
   */
  whois(params: SeoWhoisParams, options?: RequestOptions): Promise<JsonObject> {
    return this.client.request({ method: "GET", path: "/v1/seo/whois", query: { url: params.url } }, options) as Promise<JsonObject>;
  }

  /**
   * How long a domain has been registered.
   *
   * A projection of the WHOIS record — the registration and expiry dates and the age
   * derived from them, without the rest of the record.
   */
  domainAge(params: SeoDomainAgeParams, options?: RequestOptions): Promise<JsonObject> {
    return this.client.request({ method: "GET", path: "/v1/seo/domain-age", query: { url: params.url } }, options) as Promise<JsonObject>;
  }

  /**
   * Check a page's canonical URL.
   */
  canonical(params: SeoCanonicalParams, options?: RequestOptions): Promise<JsonObject> {
    return this.client.request({ method: "GET", path: "/v1/seo/canonical", query: { url: params.url } }, options) as Promise<JsonObject>;
  }
}

export interface DevHashParams {
  /** The plaintext to hash */
  password: string;
  /** bcrypt cost. Each step doubles the work; 12 is Laravel's default (server default: 12) */
  rounds?: number;
}

export interface DevHashVerifyParams {
  password: string;
  /** A bcrypt hash to check against */
  hash: string;
}

export interface DevJsonParams {
  /** The JSON document, as text */
  content: string;
  /** format | minify | validate (server default: 'format') */
  action?: string;
  /** Spaces per level when action=format (server default: 2) */
  indent?: number;
  /** Order object keys alphabetically (server default: False) */
  sortKeys?: boolean;
}

/** Developer utilities: bcrypt hashing, JSON validation and formatting. */
export class Dev extends Resource {
  /**
   * Hash a password with bcrypt.
   *
   * The cost is the whole point of bcrypt, so it is a parameter rather than a constant.
   * Note that it is exponential: `rounds=16` is 16x the CPU of `rounds=12` and takes a
   * noticeable fraction of a second.
   */
  hash(params: DevHashParams, options?: RequestOptions): Promise<JsonObject> {
    return this.client.request({ method: "POST", path: "/v1/dev/hash", json: { password: params.password, rounds: params.rounds } }, options) as Promise<JsonObject>;
  }

  /**
   * Check a password against a bcrypt hash.
   *
   * A malformed hash is `matches: false`, not an error — telling the caller which of the
   * two inputs was wrong is exactly what an attacker wants.
   */
  hashVerify(params: DevHashVerifyParams, options?: RequestOptions): Promise<JsonObject> {
    return this.client.request({ method: "POST", path: "/v1/dev/hash/verify", json: { password: params.password, hash: params.hash } }, options) as Promise<JsonObject>;
  }

  /**
   * Validate, format or minify JSON.
   *
   * A syntax error comes back as `valid: false` with the line and column, and HTTP 200 —
   * the request itself was well-formed, and "this document is invalid" is the answer,
   * not a failure to answer.
   */
  json(params: DevJsonParams, options?: RequestOptions): Promise<JsonObject> {
    return this.client.request({ method: "POST", path: "/v1/dev/json", json: { content: params.content, action: params.action, indent: params.indent, sort_keys: params.sortKeys } }, options) as Promise<JsonObject>;
  }
}

export interface GlbInspectParams {
  /** The first bytes of the .glb, as a file part: its 12-byte header, its JSON chunk, and the 8-byte header of the chunk after it. That is `file.slice(0, 20 + jsonLength + 8)`, where jsonLength is the little-endian uint32 at byte 12. Never the whole file */
  head: FileInput;
  /** The length of the whole .glb in bytes */
  size: number;
}

export interface GlbPlanParams {
  /** The first bytes of the .glb, as a file part: its 12-byte header, its JSON chunk, and the 8-byte header of the chunk after it. That is `file.slice(0, 20 + jsonLength + 8)`, where jsonLength is the little-endian uint32 at byte 12. Never the whole file */
  head: FileInput;
  /** The length of the whole .glb in bytes */
  size: number;
  /** JSON: `{"ops": [...], "cleanup": {...}, "removal": "required" | "unlink", "mode": "plan" | "check"}`. An operation names things by their index in the file as it arrived */
  edit: string;
  /** PNG or JPEG file parts an operation puts into the model. Each part's FILENAME is the name an operation refers to it by */
  images?: FileInput[];
  /** JSON `{"<image index>": "<sha-256, 64 lowercase hex>"}`, each computed by the caller over the image's own bytes. Needed only when `cleanup.dedupe` is asked for */
  hashes?: string;
}

export interface GlbImageParams {
  /** One PNG or JPEG */
  image: FileInput;
  /** The longest side, in pixels, of the picture that comes back */
  maxSize?: number;
  /** The quality a JPEG is written at */
  jpegQuality?: number;
  /** Allow a PNG with no transparency to come back as a JPEG. Only where inspect says `jpeg_allowed` for that image */
  toJpeg?: boolean;
}

/** 3D model (.glb) inspection and editing plans. Needs the Enterprise plan. */
export class Glb extends Resource {
  /**
   * Every limit of the GLB routes.
   *
   * The numbers the three routes below hold a request to: the largest scene description,
   * how many operations one edit may carry, how many images and of what size, how long
   * one request may run. Read it once and check before you send; the numbers can change
   * without a new version of this API.
   */
  limits(options?: RequestOptions): Promise<JsonObject> {
    return this.client.request({ method: "GET", path: "/v1/glb/limits" }, options) as Promise<JsonObject>;
  }

  /**
   * What a .glb is, and what may be done to it.
   *
   * Send the model's **head** and its size; the model itself is never sent.
   */
  inspect(params: GlbInspectParams, options?: RequestOptions): Promise<JsonObject> {
    return this.client.request({ method: "POST", path: "/v1/glb/inspect", files: { head: params.head }, form: { size: params.size }, multipart: true }, options) as Promise<JsonObject>;
  }

  /**
   * Compile edits to a .glb into a plan of byte ranges.
   *
   * Answers `{"segments": [...], "total": N, "report": {...}}`. **You build the edited
   * file** by concatenating the segments in order:
   */
  plan(params: GlbPlanParams, options?: RequestOptions): Promise<JsonObject> {
    return this.client.request({ method: "POST", path: "/v1/glb/plan", files: { head: params.head, images: params.images }, form: { size: params.size, edit: params.edit, hashes: params.hashes }, multipart: true }, options) as Promise<JsonObject>;
  }

  /**
   * Shrink one texture.
   *
   * A smaller picture comes back as bytes (`image/png` or `image/jpeg`) with `X-Glb-*`
   * headers saying what was done. A picture that was left alone comes back as JSON,
   * `{"changed": false, "outcome": "..."}`, with one word saying why. The ranges
   * `max_size` and `jpeg_quality` may take are in `GET /v1/glb/limits`.
   */
  image(params: GlbImageParams, options?: RequestOptions): Promise<unknown> {
    return this.client.request({ method: "POST", path: "/v1/glb/image", files: { image: params.image }, form: { max_size: params.maxSize, jpeg_quality: params.jpegQuality, to_jpeg: params.toJpeg }, multipart: true }, options) as Promise<unknown>;
  }
}

/** Status and result of work submitted with mode="async". */
export class Jobs extends Resource {
  /**
   * Check the status of an async job.
   *
   * Poll this until `status` is `succeeded` or `failed`. A second or two between polls
   * is plenty; the work is measured in seconds, not milliseconds.
   */
  get(jobId: string, options?: RequestOptions): Promise<JsonObject> {
    return this.client.request({ method: "GET", path: `/v1/jobs/${seg(jobId)}` }, options) as Promise<JsonObject>;
  }

  /**
   * Download a finished job's output.
   */
  result(jobId: string, options?: RequestOptions): Promise<DipsacFile> {
    return this.client.request({ method: "GET", path: `/v1/jobs/${seg(jobId)}/result` }, options) as Promise<DipsacFile>;
  }
}

export interface AiBuiltinVoicesParams {
  /** Language code, e.g. en, hi (server default: 'en') */
  language?: string;
}

export interface AiTranscribeParams {
  /** The audio or video file */
  file: FileInput;
  /** Language code, e.g. en, hi */
  language?: string;
  /** Label who is speaking (server default: False) */
  diarize?: boolean;
  /** Translate the transcript into English (server default: False) */
  translate?: boolean;
}

export interface AiTranscribeVideoParams {
  /** The audio or video file */
  file: FileInput;
  /** Language code, e.g. en, hi */
  language?: string;
  /** Label who is speaking (server default: False) */
  diarize?: boolean;
  /** Translate the transcript into English (server default: False) */
  translate?: boolean;
}

export interface AiSubtitlesParams {
  /** The audio or video file */
  file: FileInput;
  /** Language code, e.g. en, hi */
  language?: string;
  /** Output format (server default: 'srt') */
  fmt?: string;
}

export interface AiSpeakParams {
  /** The text to speak */
  text: string;
  /** Language code, e.g. en, hi (server default: 'en') */
  language?: string;
  /** A built-in voice, by name (see builtin_voices) */
  voice?: string;
  /** A cloned voice you registered, by name */
  clonedVoice?: string;
  /** Speaking rate; 1.0 is normal (server default: 1.0) */
  speed?: number;
  /** Speaking style, where the voice supports one */
  style?: string;
  /** Output format (server default: 'wav') */
  fmt?: string;
  /** Return a Job at once and synthesise in the background (server default: False) */
  background?: boolean;
}

export interface AiLibraryParams {
  /** Only this kind of generation */
  kind?: string;
  /** How many to return (server default: 30) */
  limit?: number;
  /** Return items older than this id */
  beforeId?: number;
  /** Only items whose text contains this */
  search?: string;
}

export interface AiLibraryAudioParams {
  /** Download format, e.g. mp3 */
  format?: string;
}

export interface AiRegisterVoiceParams {
  /** A name for the voice */
  name: string;
  /** The audio or video file */
  file: FileInput;
  /** The speaker's consent statement */
  consent?: string;
}

/** AI Voice Studio: text to speech, transcription, subtitles, cloned voices. */
export class Ai extends Resource {
  /**
   * What this account may do in the AI Voice Studio, and what it has used.
   */
  status(options?: RequestOptions): Promise<JsonObject> {
    return this.client.request({ method: "GET", path: "/ai/status" }, options) as Promise<JsonObject>;
  }

  /**
   * The studio's plans, limits and prices.
   */
  pricing(options?: RequestOptions): Promise<JsonObject> {
    return this.client.request({ method: "GET", path: "/ai/pricing" }, options) as Promise<JsonObject>;
  }

  /**
   * The built-in voices, optionally for one language.
   */
  builtinVoices(params: AiBuiltinVoicesParams = {}, options?: RequestOptions): Promise<JsonObject> {
    return this.client.request({ method: "GET", path: "/ai/voices/builtin", query: { language: params.language } }, options) as Promise<JsonObject>;
  }

  /**
   * Turn an audio file into text.
   */
  transcribe(params: AiTranscribeParams, options?: RequestOptions): Promise<JsonObject> {
    return this.client.request({ method: "POST", path: "/ai/transcribe", files: { file: params.file }, form: { language: params.language, diarize: params.diarize, translate: params.translate }, multipart: true }, options) as Promise<JsonObject>;
  }

  /**
   * Turn the speech in a video file into text.
   */
  transcribeVideo(params: AiTranscribeVideoParams, options?: RequestOptions): Promise<JsonObject> {
    return this.client.request({ method: "POST", path: "/ai/transcribe/video", files: { file: params.file }, form: { language: params.language, diarize: params.diarize, translate: params.translate }, multipart: true }, options) as Promise<JsonObject>;
  }

  /**
   * Make a subtitle file (SRT or VTT) from audio or video.
   */
  subtitles(params: AiSubtitlesParams, options?: RequestOptions): Promise<DipsacFile> {
    return this.client.request({ method: "POST", path: "/ai/subtitles", files: { file: params.file }, form: { language: params.language, fmt: params.fmt }, multipart: true }, options) as Promise<DipsacFile>;
  }

  /**
   * Turn text into speech. With background=True it returns a Job to wait on, which is the way to synthesise long text.
   *
   * Resolves to a Job instead of the result when the work is sent to the
   * background; await its wait() for the result.
   */
  speak(params: AiSpeakParams, options?: RequestOptions): Promise<DipsacFile | Job> {
    return this.client.request({ method: "POST", path: "/ai/speak", form: { text: params.text, language: params.language, voice: params.voice, cloned_voice: params.clonedVoice, speed: params.speed, style: params.style, fmt: params.fmt, async: params.background } }, options) as Promise<DipsacFile | Job>;
  }

  /**
   * The state of a background speech job, as the API reports it.
   */
  job(jobId: string, options?: RequestOptions): Promise<JsonObject> {
    return this.client.request({ method: "GET", path: `/ai/jobs/${seg(jobId)}` }, options) as Promise<JsonObject>;
  }

  /**
   * List what this account has generated.
   */
  library(params: AiLibraryParams = {}, options?: RequestOptions): Promise<JsonObject> {
    return this.client.request({ method: "GET", path: "/ai/library", query: { kind: params.kind, limit: params.limit, before_id: params.beforeId, search: params.search } }, options) as Promise<JsonObject>;
  }

  /**
   * One generation from the library, with its details.
   */
  libraryItem(genId: number, options?: RequestOptions): Promise<JsonObject> {
    return this.client.request({ method: "GET", path: `/ai/library/${seg(genId)}` }, options) as Promise<JsonObject>;
  }

  /**
   * Delete one generation from the library.
   */
  deleteLibraryItem(genId: number, options?: RequestOptions): Promise<JsonObject> {
    return this.client.request({ method: "DELETE", path: `/ai/library/${seg(genId)}` }, options) as Promise<JsonObject>;
  }

  /**
   * Download the audio of one generation.
   */
  libraryAudio(genId: number, params: AiLibraryAudioParams = {}, options?: RequestOptions): Promise<DipsacFile> {
    return this.client.request({ method: "GET", path: `/ai/library/${seg(genId)}/audio`, query: { format: params.format } }, options) as Promise<DipsacFile>;
  }

  /**
   * The cloned voices this account has registered.
   */
  voices(options?: RequestOptions): Promise<JsonObject> {
    return this.client.request({ method: "GET", path: "/ai/voices" }, options) as Promise<JsonObject>;
  }

  /**
   * Register a cloned voice from a recording of the speaker.
   */
  registerVoice(params: AiRegisterVoiceParams, options?: RequestOptions): Promise<JsonObject> {
    return this.client.request({ method: "POST", path: "/ai/voices", files: { file: params.file }, form: { name: params.name, consent: params.consent }, multipart: true }, options) as Promise<JsonObject>;
  }

  /**
   * Erase a cloned voice.
   */
  deleteVoice(voiceId: number, options?: RequestOptions): Promise<JsonObject> {
    return this.client.request({ method: "DELETE", path: `/ai/voices/${seg(voiceId)}` }, options) as Promise<JsonObject>;
  }
}

export const OPERATIONS: ReadonlyArray<readonly [string, string, string, string]> = [
  ["POST", "/v1/pdf/merge", "pdf", "merge"],
  ["POST", "/v1/pdf/split", "pdf", "split"],
  ["POST", "/v1/pdf/delete-pages", "pdf", "deletePages"],
  ["POST", "/v1/pdf/rotate", "pdf", "rotate"],
  ["POST", "/v1/pdf/compress", "pdf", "compress"],
  ["POST", "/v1/pdf/convert", "pdf", "convert"],
  ["POST", "/v1/pdf/from-office", "pdf", "fromOffice"],
  ["POST", "/v1/pdf/protect", "pdf", "protect"],
  ["POST", "/v1/pdf/unlock", "pdf", "unlock"],
  ["POST", "/v1/pdf/watermark", "pdf", "watermark"],
  ["POST", "/v1/pdf/metadata", "pdf", "metadata"],
  ["POST", "/v1/image/convert", "image", "convert"],
  ["POST", "/v1/image/compress", "image", "compress"],
  ["POST", "/v1/image/resize", "image", "resize"],
  ["POST", "/v1/image/crop", "image", "crop"],
  ["POST", "/v1/image/remove-background", "image", "removeBackground"],
  ["POST", "/v1/image/to-pdf", "image", "toPdf"],
  ["POST", "/v1/image/info", "image", "info"],
  ["POST", "/v1/audio/convert", "audio", "convert"],
  ["POST", "/v1/audio/normalize", "audio", "normalize"],
  ["POST", "/v1/audio/merge", "audio", "merge"],
  ["POST", "/v1/video/convert", "video", "convert"],
  ["POST", "/v1/video/extract-audio", "video", "extractAudio"],
  ["POST", "/v1/video/cut", "video", "cut"],
  ["POST", "/v1/video/resize", "video", "resize"],
  ["POST", "/v1/video/mute", "video", "mute"],
  ["POST", "/v1/seo/meta", "seo", "meta"],
  ["GET", "/v1/seo/ssl", "seo", "ssl"],
  ["GET", "/v1/seo/redirects", "seo", "redirects"],
  ["GET", "/v1/seo/whois", "seo", "whois"],
  ["GET", "/v1/seo/domain-age", "seo", "domainAge"],
  ["GET", "/v1/seo/canonical", "seo", "canonical"],
  ["POST", "/v1/dev/hash", "dev", "hash"],
  ["POST", "/v1/dev/hash/verify", "dev", "hashVerify"],
  ["POST", "/v1/dev/json", "dev", "json"],
  ["GET", "/v1/glb/limits", "glb", "limits"],
  ["POST", "/v1/glb/inspect", "glb", "inspect"],
  ["POST", "/v1/glb/plan", "glb", "plan"],
  ["POST", "/v1/glb/image", "glb", "image"],
  ["GET", "/v1/jobs/{job_id}", "jobs", "get"],
  ["GET", "/v1/jobs/{job_id}/result", "jobs", "result"],
  ["GET", "/ai/status", "ai", "status"],
  ["GET", "/ai/pricing", "ai", "pricing"],
  ["GET", "/ai/voices/builtin", "ai", "builtinVoices"],
  ["POST", "/ai/transcribe", "ai", "transcribe"],
  ["POST", "/ai/transcribe/video", "ai", "transcribeVideo"],
  ["POST", "/ai/subtitles", "ai", "subtitles"],
  ["POST", "/ai/speak", "ai", "speak"],
  ["GET", "/ai/jobs/{job_id}", "ai", "job"],
  ["GET", "/ai/library", "ai", "library"],
  ["GET", "/ai/library/{gen_id}", "ai", "libraryItem"],
  ["DELETE", "/ai/library/{gen_id}", "ai", "deleteLibraryItem"],
  ["GET", "/ai/library/{gen_id}/audio", "ai", "libraryAudio"],
  ["GET", "/ai/voices", "ai", "voices"],
  ["POST", "/ai/voices", "ai", "registerVoice"],
  ["DELETE", "/ai/voices/{voice_id}", "ai", "deleteVoice"],
];
