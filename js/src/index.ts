// The official JavaScript and TypeScript library for the DIPSAC API.
//
//     import { Dipsac } from "dipsac";
//     const client = new Dipsac({ apiKey: "dps_..." });
//
// Docs: https://dipsac.com/dashboard/reference
export { Dipsac, DEFAULT_BASE_URL } from "./client.js";
export type { DipsacOptions, RequestOptions, RequestSpec } from "./client.js";
export { DipsacFile, Job } from "./models.js";
export type { JsonObject, WaitOptions } from "./models.js";
export type { FileInput } from "./files.js";
export * from "./errors.js";
export * from "./resources.js";
export { VERSION } from "./version.js";
