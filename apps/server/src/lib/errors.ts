import type { ContentfulStatusCode } from 'hono/utils/http-status';

/** Application error with an HTTP status and a stable machine-readable code. */
export class AppError extends Error {
  readonly status: ContentfulStatusCode;
  readonly code: string;

  constructor(status: ContentfulStatusCode, code: string, message: string) {
    super(message);
    this.name = 'AppError';
    this.status = status;
    this.code = code;
  }

  static unauthorized(message = 'Authentication required') {
    return new AppError(401, 'unauthenticated', message);
  }

  static forbidden(message = 'Not allowed') {
    return new AppError(403, 'forbidden', message);
  }

  static notFound(message = 'Not found') {
    return new AppError(404, 'not_found', message);
  }

  static badRequest(message: string, code = 'bad_request') {
    return new AppError(400, code, message);
  }

  static conflict(message: string) {
    return new AppError(409, 'conflict', message);
  }

  static payloadTooLarge(message: string) {
    return new AppError(413, 'payload_too_large', message);
  }

  static unsupportedMedia(message: string) {
    return new AppError(415, 'unsupported_media_type', message);
  }

  static tooManyRequests(message = 'Too many requests') {
    return new AppError(429, 'rate_limited', message);
  }

  static internal(message = 'Internal server error') {
    return new AppError(500, 'internal_error', message);
  }
}
