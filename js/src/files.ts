// Turning what a caller hands over into one part of an upload.
//
// THE NAME MATTERS. The API decides what a file is by the extension of its name
// and refuses one it does not expect. A path and a File carry their own name.
// Bare bytes carry none, so their type is read from how they begin; for anything
// that cannot be told that way (a Word file, for one) pass { data, filename }.
//
// EVERY UPLOAD IS A Blob OF KNOWN SIZE BEFORE IT IS SENT. The API requires a
// Content-Length on uploads and answers 411 to a chunked body; a FormData made
// of Blobs has a length, a stream does not.

/** What a method that takes a file accepts. */
export type FileInput =
  | string // a path on disk (Node.js)
  | Blob // includes File
  | Uint8Array
  | ArrayBuffer
  | { data: Blob | Uint8Array | ArrayBuffer; filename: string; contentType?: string };

const TYPES: Record<string, string> = {
  pdf: "application/pdf",
  png: "image/png",
  jpg: "image/jpeg",
  jpeg: "image/jpeg",
  webp: "image/webp",
  gif: "image/gif",
  bmp: "image/bmp",
  tiff: "image/tiff",
  mp3: "audio/mpeg",
  wav: "audio/wav",
  ogg: "audio/ogg",
  flac: "audio/flac",
  m4a: "audio/mp4",
  aac: "audio/aac",
  mp4: "video/mp4",
  mov: "video/quicktime",
  webm: "video/webm",
  mkv: "video/x-matroska",
  avi: "video/x-msvideo",
  docx: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  xlsx: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  pptx: "application/vnd.openxmlformats-officedocument.presentationml.presentation",
  glb: "model/gltf-binary",
  json: "application/json",
  txt: "text/plain",
};

const starts = (b: Uint8Array, ...bytes: number[]): boolean => bytes.every((v, i) => b[i] === v);
const ascii = (b: Uint8Array, from: number, text: string): boolean =>
  [...text].every((ch, i) => b[from + i] === ch.charCodeAt(0));

/** An extension for bytes that came with no name, or undefined. */
function sniff(b: Uint8Array): string | undefined {
  if (ascii(b, 0, "%PDF")) return "pdf";
  if (starts(b, 0x89, 0x50, 0x4e, 0x47)) return "png";
  if (starts(b, 0xff, 0xd8, 0xff)) return "jpg";
  if (ascii(b, 0, "GIF8")) return "gif";
  if (ascii(b, 0, "RIFF") && ascii(b, 8, "WEBP")) return "webp";
  if (ascii(b, 0, "RIFF") && ascii(b, 8, "WAVE")) return "wav";
  if (ascii(b, 0, "ID3") || starts(b, 0xff, 0xfb) || starts(b, 0xff, 0xf3)) return "mp3";
  if (ascii(b, 0, "OggS")) return "ogg";
  if (ascii(b, 0, "fLaC")) return "flac";
  if (ascii(b, 0, "glTF")) return "glb";
  if (starts(b, 0x1a, 0x45, 0xdf, 0xa3)) return "webm";
  if (ascii(b, 4, "ftyp")) return "mp4";
  return undefined;
}

const typeFor = (filename: string): string =>
  TYPES[filename.slice(filename.lastIndexOf(".") + 1).toLowerCase()] ?? "application/octet-stream";

const baseName = (path: string): string => path.split(/[\\/]/).pop() || path;

async function head(blob: Blob): Promise<Uint8Array> {
  return new Uint8Array(await blob.slice(0, 16).arrayBuffer());
}

/** One uploaded file as a Blob with a name. */
export async function toPart(value: FileInput, field = "file"): Promise<{ blob: Blob; filename: string }> {
  let data: Blob | Uint8Array | ArrayBuffer;
  let filename: string | undefined;
  let contentType: string | undefined;

  if (typeof value === "string") {
    const { readFile } = await import("node:fs/promises");
    data = await readFile(value);
    filename = baseName(value);
  } else if (value instanceof Blob || value instanceof Uint8Array || value instanceof ArrayBuffer) {
    data = value;
    const name = (value as { name?: unknown }).name;
    if (typeof name === "string" && name) filename = baseName(name);
  } else if (value && typeof value === "object" && "data" in value && typeof value.filename === "string") {
    data = value.data;
    filename = baseName(value.filename);
    contentType = value.contentType;
  } else {
    throw new TypeError(
      "cannot upload this value; pass a path, a Blob or File, a Uint8Array, an ArrayBuffer, or { data, filename }",
    );
  }

  const raw = data instanceof Blob ? data : new Blob([data as BlobPart]);
  if (!filename) {
    const ext = sniff(await head(raw));
    filename = ext ? `${field}.${ext}` : field;
  }
  const type = contentType ?? (raw.type || typeFor(filename));
  const blob = raw.type === type ? raw : new Blob([raw], { type });
  return { blob, filename };
}
