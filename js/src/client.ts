// The transport: auth, uploads, errors, retries. One method per endpoint lives in
// resources.ts, which is generated; everything here is what those methods share.
//
// WHAT IS RETRIED, AND WHAT IS DELIBERATELY NOT.
//
//   * A 429 whose Retry-After is short (the per-second limit; the Free plan
//     allows two requests a second) is waited out and sent again. The API
//     refused it before doing any work, so sending it again cannot do the work
//     twice.
//   * A 429 that asks for a long wait is the plan's MONTHLY limit. Waiting a day
//     inside a function call helps nobody, so it is thrown at once.
//   * A GET that got 502, 503 or 504, or whose request failed, is tried again.
//   * A POST that got a 5xx, or whose request failed, is NOT. fetch does not say
//     whether a failed request reached the server, and some of the work (speech)
//     is paid for per call.
import { APIConnectionError, APITimeoutError, DipsacError, errorFor } from "./errors.js";
import { toPart, type FileInput } from "./files.js";
import { DipsacFile, Job, filenameFrom, type JsonObject } from "./models.js";
import { Ai, Audio, Dev, Glb, Image, Jobs, Pdf, Seo, Video } from "./resources.js";
import { VERSION } from "./version.js";

export const DEFAULT_BASE_URL = "https://api.dipsac.com";
const DEFAULT_TIMEOUT = 300_000;
const DEFAULT_MAX_RETRIES = 2;
// The longest Retry-After worth sleeping through, in seconds. The per-second
// limit asks for 1; the monthly limit asks for 86400.
const MAX_RETRY_AFTER = 30;

export interface DipsacOptions {
  /** Your key (`dps_...`). Read from the DIPSAC_API_KEY environment variable when left out. */
  apiKey?: string;
  /** The API's address; https://api.dipsac.com unless set. */
  baseUrl?: string;
  /** Milliseconds to wait for an answer (default 300000; conversions take time). */
  timeout?: number;
  /** How many times a refused or failed request is tried again (default 2). */
  maxRetries?: number;
  /** Extra headers for every request. */
  defaultHeaders?: Record<string, string>;
  /** Your own fetch, e.g. for a proxy. */
  fetch?: typeof fetch;
}

export interface RequestOptions {
  /** Milliseconds to wait for this call. */
  timeout?: number;
  /** Abort the call. */
  signal?: AbortSignal;
}

export interface RequestSpec {
  method: string;
  path: string;
  query?: Record<string, unknown>;
  json?: Record<string, unknown>;
  form?: Record<string, unknown>;
  files?: Record<string, FileInput | FileInput[] | undefined>;
  multipart?: boolean;
}

const env = (name: string): string | undefined =>
  typeof process !== "undefined" && process.env ? process.env[name] : undefined;

const given = (v: unknown): boolean => v !== undefined && v !== null;
const scalar = (v: unknown): string => (typeof v === "boolean" ? (v ? "true" : "false") : String(v));
const sleep = (ms: number): Promise<void> => new Promise((r) => setTimeout(r, ms));

/**
 * The DIPSAC API.
 *
 *     import { Dipsac } from "dipsac";
 *
 *     const client = new Dipsac({ apiKey: "dps_..." });   // or set DIPSAC_API_KEY
 *     const merged = await client.pdf.merge({ files: ["a.pdf", "b.pdf"] });
 *     await merged.save("merged.pdf");
 */
export class Dipsac {
  readonly baseUrl: string;
  readonly timeout: number;
  readonly maxRetries: number;
  private readonly headers: Record<string, string>;
  private readonly fetchImpl: typeof fetch;

  readonly pdf: Pdf;
  readonly image: Image;
  readonly audio: Audio;
  readonly video: Video;
  readonly seo: Seo;
  readonly dev: Dev;
  readonly glb: Glb;
  readonly jobs: Jobs;
  readonly ai: Ai;

  constructor(options: DipsacOptions | string = {}) {
    const opts: DipsacOptions = typeof options === "string" ? { apiKey: options } : options;
    const apiKey = opts.apiKey ?? env("DIPSAC_API_KEY");
    if (!apiKey) {
      throw new DipsacError(
        'No API key. Pass { apiKey: "dps_..." } or set the DIPSAC_API_KEY environment variable. ' +
          "Keys are made at https://dipsac.com/dashboard/keys",
      );
    }
    this.baseUrl = (opts.baseUrl ?? env("DIPSAC_BASE_URL") ?? DEFAULT_BASE_URL).replace(/\/+$/, "");
    this.timeout = opts.timeout ?? DEFAULT_TIMEOUT;
    this.maxRetries = Math.max(0, Math.trunc(opts.maxRetries ?? DEFAULT_MAX_RETRIES));
    this.headers = { "X-API-Key": apiKey, "User-Agent": `dipsac-node/${VERSION}`, Accept: "*/*", ...opts.defaultHeaders };
    const f = opts.fetch ?? globalThis.fetch;
    if (typeof f !== "function") {
      throw new DipsacError("No fetch in this runtime. Use Node.js 18 or newer, or pass { fetch }.");
    }
    this.fetchImpl = f.bind(globalThis);

    this.pdf = new Pdf(this);
    this.image = new Image(this);
    this.audio = new Audio(this);
    this.video = new Video(this);
    this.seo = new Seo(this);
    this.dev = new Dev(this);
    this.glb = new Glb(this);
    this.jobs = new Jobs(this);
    this.ai = new Ai(this);
  }

  /** A handle on a /v1 job you already have the id of. Makes no request. */
  job(jobId: string): Job {
    return new Job(this, { job_id: jobId, status_url: `/v1/jobs/${jobId}` });
  }

  /** Send one request. The generated methods call this; so can you, for an endpoint newer than this library. */
  async request(spec: RequestSpec, options: RequestOptions = {}): Promise<unknown> {
    const method = spec.method.toUpperCase();
    const url = new URL(/^https?:\/\//.test(spec.path) ? spec.path : this.baseUrl + spec.path);
    for (const [k, v] of Object.entries(spec.query ?? {})) if (given(v)) url.searchParams.set(k, scalar(v));

    const headers: Record<string, string> = { ...this.headers };
    let body: BodyInit | undefined;
    const fields = Object.entries(spec.form ?? {}).filter(([, v]) => given(v));
    const files = Object.entries(spec.files ?? {}).filter(([, v]) => given(v));
    if (spec.json) {
      headers["Content-Type"] = "application/json";
      body = JSON.stringify(Object.fromEntries(Object.entries(spec.json).filter(([, v]) => given(v))));
    } else if (files.length) {
      // Built ONCE and reused across retries: every part is a Blob, which can be read again.
      const fd = new FormData();
      for (const [k, v] of fields) fd.append(k, scalar(v));
      for (const [name, value] of files) {
        for (const one of Array.isArray(value) ? value : [value as FileInput]) {
          const part = await toPart(one, name);
          fd.append(name, part.blob, part.filename);
        }
      }
      body = fd;
    } else if (fields.length) {
      body = new URLSearchParams(fields.map(([k, v]) => [k, scalar(v)] as [string, string]));
    }

    const timeout = options.timeout ?? this.timeout;
    for (let attempt = 0; ; attempt++) {
      let response: Response | undefined;
      let failure: unknown;
      const timer = new AbortController();
      const onAbort = (): void => timer.abort(options.signal?.reason);
      options.signal?.addEventListener("abort", onAbort, { once: true });
      let timedOut = false;
      const handle = setTimeout(() => {
        timedOut = true;
        timer.abort();
      }, timeout);
      try {
        response = await this.fetchImpl(url, { method, headers, body, signal: timer.signal, redirect: "manual" });
      } catch (err) {
        failure = err;
      }
      let wait: number | undefined;
      if (response) {
        wait = this.retryIn(attempt, method, response);
        if (wait === undefined) {
          try {
            return await this.parse(response);
          } finally {
            clearTimeout(handle);
            options.signal?.removeEventListener("abort", onAbort);
          }
        }
        await response.arrayBuffer().catch(() => undefined); // free the connection before the retry
      }
      clearTimeout(handle);
      options.signal?.removeEventListener("abort", onAbort);
      if (!response) {
        if (options.signal?.aborted) throw failure;
        const retry = attempt < this.maxRetries && method === "GET";
        if (!retry) {
          if (timedOut) throw new APITimeoutError(`No answer from the API within ${timeout} ms.`);
          const why = failure instanceof Error ? ((failure.cause as Error | undefined)?.message ?? failure.message) : String(failure);
          throw new APIConnectionError(`Could not reach the API (${why}).`);
        }
        wait = Math.min(8000, 500 * 2 ** attempt) * (0.75 + Math.random() / 2);
      }
      await sleep(wait as number);
    }
  }

  /** Milliseconds to wait before another try, or undefined to stop. See the header. */
  private retryIn(attempt: number, method: string, response: Response): number | undefined {
    if (attempt >= this.maxRetries) return undefined;
    if (response.status === 429) {
      const asked = Number(response.headers.get("retry-after") ?? "1");
      const seconds = Number.isFinite(asked) ? asked : 1;
      return seconds <= MAX_RETRY_AFTER ? Math.max(seconds, 0.2) * 1000 : undefined;
    }
    if ([502, 503, 504].includes(response.status) && method === "GET") {
      return Math.min(8000, 500 * 2 ** attempt) * (0.75 + Math.random() / 2);
    }
    return undefined;
  }

  private async parse(response: Response): Promise<unknown> {
    const headers: Record<string, string> = {};
    response.headers.forEach((v, k) => {
      headers[k.toLowerCase()] = v;
    });
    const ctype = (headers["content-type"] ?? "").split(";")[0]!.trim().toLowerCase();
    const isJson = ctype === "application/json" || ctype.endsWith("+json");
    if (response.status >= 400) {
      const text = await response.text();
      let body: unknown = text;
      if (isJson) {
        try {
          body = JSON.parse(text);
        } catch {
          /* keep the text */
        }
      }
      throw errorFor(response.status, body, headers);
    }
    if (isJson) {
      const data = (await response.json()) as JsonObject;
      if (response.status === 202 && data && typeof data === "object" && data.job_id) return new Job(this, data);
      return data;
    }
    const data = new Uint8Array(await response.arrayBuffer());
    if (!data.byteLength) return undefined;
    return new DipsacFile(data, {
      contentType: ctype || "application/octet-stream",
      filename: filenameFrom(headers["content-disposition"]),
      headers,
    });
  }
}
