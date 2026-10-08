// Two builds of one source: ES modules in dist/esm, CommonJS in dist/cjs. The
// package is "type": "module", so dist/cjs gets its own package.json saying its
// .js files are CommonJS; without it `require("dipsac")` loads them as ESM and fails.
//
// tsc is run through node by its own file, not through node_modules/.bin: that
// shim is a .cmd on Windows and a shell script elsewhere, and this is one line
// that works on both.
import { execFileSync } from "node:child_process";
import { mkdirSync, rmSync, writeFileSync } from "node:fs";

rmSync("dist", { recursive: true, force: true });
for (const project of ["tsconfig.json", "tsconfig.cjs.json"]) {
  execFileSync(process.execPath, ["node_modules/typescript/bin/tsc", "-p", project], { stdio: "inherit" });
}
mkdirSync("dist/cjs", { recursive: true });
writeFileSync("dist/cjs/package.json", JSON.stringify({ type: "commonjs" }) + "\n");
console.log("built dist/esm and dist/cjs");
