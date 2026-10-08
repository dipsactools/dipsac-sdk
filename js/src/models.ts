// What a call resolves to when the answer is not plain JSON: a file, or a job.
import { JobFailedError, JobTimeoutError } from "./errors.js";

export type JsonObject = Record<string, any>; // eslint-disable-line @typescript-eslint/no-explicit-any

/** The one thing a Job needs from the client, said here to avoid a circular import. */
export interface Requester {
  request(spec: { method: string; path: string }, options?: { timeout?: number; signal?: AbortSignal }): Promise<unknown>;
}

/** The name in a Content-Disposition header, preferring the UTF-8 form. */
export function filenameFrom(disposition: string | undefined | null): string | undefined {
  const raw = disposition ?? "";
  const base = (p: string): string => p.split(/[\\/]/).pop() || p;
  const star = /filename\*\s*=\s*utf-8''([^;]+)/i.exec(raw);
  if (star?.[1]) {
    try {
      return base(decodeURIComponent(star[1].trim()));
    } catch {
      /* fall through to the plain form */
    }
  }
  const plain = /filename\s*=\s*"([^"]*)"/i.exec(raw) ?? /filename\s*=\s*([^;]+)/i.exec(raw);
  return plain?.[1] ? base(plain[1].trim()) : undefined;
}

/** A file the API returned. */
export class DipsacFile {
  /** The bytes. */
  readonly data: Uint8Array;
  /** e.g. `application/pdf`. */
  readonly contentType: string;
  /** The name the API gave it, when it gave one. */
  readonly filename?: string;
  /** The response headers (lower-case names). */
  readonly headers: Record<string, string>;

  constructor(data: Uint8Array, init: { contentType?: string; filename?: string; headers?: Record<string, string> } = {}) {
    this.data = data;
    this.contentType = init.contentType ?? "application/octet-stream";
    this.filename = init.filename;
    this.headers = init.headers ?? {};
  }

  get size(): number {
    return this.data.byteLength;
  }

  /** The content as text (subtitles, for one). */
  text(): string {
    return new TextDecoder("utf-8").decode(this.data);
  }

  blob(): Blob {
    return new Blob([this.data as BlobPart], { type: this.contentType });
  }

  /**
   * Write the file (Node.js) and resolve to where it went. With no path it goes
   * to the current directory under the name the API gave it; a path that is an
   * existing directory gets that name inside it.
   */
  async save(path?: string): Promise<string> {
    const fs = await import("node:fs/promises");
    const { join } = await import("node:path");
    const name = this.filename ?? "download";
    let target = path ?? name;
    if (path !== undefined) {
      const stat = await fs.stat(path).catch(() => undefined);
      if (stat?.isDirectory()) target = join(path, name);
    }
    await fs.writeFile(target, this.data);
    return target;
  }

  toString(): string {
    return `DipsacFile(${this.filename ?? "(unnamed)"}, ${this.contentType}, ${this.size} bytes)`;
  }
}

// The API's own words for where a job is. Two families share this class: /v1
// jobs end in "succeeded", speech jobs in "done".
const FINISHED = new Set(["succeeded", "done"]);
const FAILED = new Set(["failed"]);
const sleep = (ms: number): Promise<void> => new Promise((r) => setTimeout(r, ms));

export interface WaitOptions {
  /** Give up after this many milliseconds (default 600000). */
  timeout?: number;
  /** Milliseconds between checks (default 2000). */
  pollInterval?: number;
}

/**
 * Work the API is doing in the background.
 *
 *     const job = await client.video.convert({ file: "in.mov", outputFormat: "mp4", mode: "async" });
 *     const clip = await job.wait();
 *     await clip.save("out.mp4");
 */
export class Job {
  readonly id: string;
  /** The last status body the API sent. */
  raw: JsonObject;
  private readonly statusPath: string;

  constructor(
    private readonly client: Requester,
    data: JsonObject,
  ) {
    this.raw = { ...data };
    this.id = String(data.job_id ?? data.id ?? "");
    this.statusPath = String(data.status_url ?? data.poll ?? `/v1/jobs/${this.id}`);
  }

  /** queued, running, then succeeded (speech: done) or failed. */
  get status(): string {
    return String(this.raw.status ?? "queued");
  }
  get finished(): boolean {
    return FINISHED.has(this.status);
  }
  get failed(): boolean {
    return FAILED.has(this.status);
  }
  get error(): string | undefined {
    return typeof this.raw.error === "string" ? this.raw.error : undefined;
  }

  /** Ask the API where the job is now. */
  async refresh(): Promise<this> {
    const data = await this.client.request({ method: "GET", path: this.statusPath });
    if (data && typeof data === "object") Object.assign(this.raw, data);
    return this;
  }

  /** Download the output of a finished job. */
  async result(): Promise<DipsacFile> {
    const path = String(this.raw.result_url ?? this.raw.audio_url ?? `${this.statusPath.replace(/\/$/, "")}/result`);
    return (await this.client.request({ method: "GET", path })) as DipsacFile;
  }

  /**
   * Wait for the job and resolve to its output. Rejects with JobFailedError if
   * the job fails and JobTimeoutError if it is not done within `timeout`.
   */
  async wait(options: WaitOptions = {}): Promise<DipsacFile> {
    const timeout = options.timeout ?? 600_000;
    const pollInterval = options.pollInterval ?? 2_000;
    const started = Date.now();
    for (;;) {
      await this.refresh();
      if (this.finished) return this.result();
      if (this.failed) throw new JobFailedError(this.error ?? `Job ${this.id} failed.`, this);
      const waited = Date.now() - started;
      if (waited + pollInterval > timeout) {
        throw new JobTimeoutError(
          `Job ${this.id} was still ${this.status} after ${Math.round(waited / 1000)} seconds. ` +
            `It was not cancelled; call wait() again, or fetch it later by its id.`,
          this,
        );
      }
      await sleep(pollInterval);
    }
  }
}
