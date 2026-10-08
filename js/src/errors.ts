// Everything this library throws.
//
//   DipsacError
//   ├── APIConnectionError        the request never got an answer
//   │   └── APITimeoutError
//   ├── APIStatusError            the API answered with an error
//   │   ├── BadRequestError            400
//   │   ├── AuthenticationError        401  the key is missing or wrong
//   │   ├── PaymentRequiredError       402  an allowance is used up
//   │   ├── PermissionDeniedError      403  the plan does not include this
//   │   ├── NotFoundError              404
//   │   ├── ConflictError              409  e.g. a job that has not finished
//   │   ├── PayloadTooLargeError       413
//   │   ├── UnsupportedMediaTypeError  415  the wrong kind of file
//   │   ├── UnprocessableEntityError   422  a parameter is missing or invalid
//   │   ├── RateLimitError             429
//   │   └── InternalServerError        500 and above
//   ├── JobFailedError            a background job ended in failure
//   └── JobTimeoutError           wait() ran out of time; the job may still finish

export class DipsacError extends Error {
  constructor(message: string) {
    super(message);
    this.name = new.target.name;
  }
}

export class APIConnectionError extends DipsacError {}
export class APITimeoutError extends APIConnectionError {}

export interface APIErrorDetails {
  status: number;
  code?: string;
  requestId?: string;
  body?: unknown;
  headers?: Record<string, string>;
}

/** The API answered with an error status. */
export class APIStatusError extends DipsacError {
  /** The HTTP status. */
  readonly status: number;
  /** The API's short name for the error, e.g. `rate_limited`. */
  readonly code?: string;
  /** Quote this to DIPSAC support. */
  readonly requestId?: string;
  /** The whole response body, parsed if it was JSON. */
  readonly body: unknown;
  /** The response headers (lower-case names). */
  readonly headers: Record<string, string>;

  constructor(message: string, details: APIErrorDetails) {
    super(message);
    this.status = details.status;
    this.code = details.code;
    this.requestId = details.requestId;
    this.body = details.body;
    this.headers = details.headers ?? {};
  }

  protected field<T>(name: string): T | undefined {
    const body = this.body;
    return body && typeof body === "object" ? ((body as Record<string, unknown>)[name] as T) : undefined;
  }
}

export class BadRequestError extends APIStatusError {}
export class AuthenticationError extends APIStatusError {}
/** An allowance or quota is used up; `body` carries the numbers. */
export class PaymentRequiredError extends APIStatusError {}
/** The key's plan does not include this endpoint. */
export class PermissionDeniedError extends APIStatusError {
  get requiredPlan(): string | undefined {
    return this.field<string>("required_plan");
  }
  get currentPlan(): string | undefined {
    return this.field<string>("current_plan");
  }
}
export class NotFoundError extends APIStatusError {}
export class ConflictError extends APIStatusError {}
export class PayloadTooLargeError extends APIStatusError {}
export class UnsupportedMediaTypeError extends APIStatusError {
  /** The file types this endpoint takes. */
  get accepted(): string[] | undefined {
    return this.field<string[]>("accepted");
  }
}
export class UnprocessableEntityError extends APIStatusError {
  /** Which parameters were refused, and why. */
  get fields(): Array<Record<string, unknown>> | undefined {
    return this.field<Array<Record<string, unknown>>>("fields");
  }
}
/**
 * Too many requests. `retryAfter` is how many seconds the API asked to wait: a
 * second or two is the per-second limit, a day is the plan's monthly limit.
 */
export class RateLimitError extends APIStatusError {
  get retryAfter(): number | undefined {
    const raw = this.headers["retry-after"];
    const n = raw === undefined ? NaN : Number(raw);
    return Number.isFinite(n) ? n : undefined;
  }
}
export class InternalServerError extends APIStatusError {}

/** A background job ended in failure. `job` is the job, with its last status. */
export class JobFailedError extends DipsacError {
  constructor(message: string, readonly job?: unknown) {
    super(message);
  }
}
/** wait() gave up. The job itself was not cancelled and may still finish. */
export class JobTimeoutError extends DipsacError {
  constructor(message: string, readonly job?: unknown) {
    super(message);
  }
}

const BY_STATUS: Record<number, typeof APIStatusError> = {
  400: BadRequestError,
  401: AuthenticationError,
  402: PaymentRequiredError,
  403: PermissionDeniedError,
  404: NotFoundError,
  409: ConflictError,
  413: PayloadTooLargeError,
  415: UnsupportedMediaTypeError,
  422: UnprocessableEntityError,
  429: RateLimitError,
};

/** The right error for an error response. */
export function errorFor(status: number, body: unknown, headers: Record<string, string>): APIStatusError {
  let code: string | undefined;
  let message: string | undefined;
  let requestId: string | undefined;
  if (body && typeof body === "object") {
    const b = body as Record<string, unknown>;
    if (typeof b.error === "string") code = b.error;
    for (const key of ["message", "detail"]) {
      const v = b[key];
      if (typeof v === "string" && v) {
        message = v;
        break;
      }
    }
    if (typeof b.request_id === "string") requestId = b.request_id;
  } else if (typeof body === "string" && body.trim()) {
    message = body.trim().slice(0, 500);
  }
  requestId = requestId ?? headers["x-request-id"];
  const Cls = BY_STATUS[status] ?? (status >= 500 ? InternalServerError : APIStatusError);
  return new Cls(message ?? `The API answered ${status}.`, { status, code, requestId, body, headers });
}
