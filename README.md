# DIPSAC SDKs

The official client libraries for the [DIPSAC API](https://dipsac.com/dashboard/reference).

| Language | Install | Source | Docs |
|---|---|---|---|
| Python 3.9+ | `pip install dipsac` | [python/](python/) | [python/README.md](python/README.md) |
| JavaScript / TypeScript (Node 18+) | `npm install dipsac` | [js/](js/) | [js/README.md](js/README.md) |

Both cover the same 56 operations: the tool API under `/v1` (PDF, image, audio,
video, SEO, developer utilities, 3D models, background jobs) and the AI Voice
Studio under `/ai`.

## How this repository is put together

```
openapi/dipsac.openapi.json   the API's own schema, a snapshot of https://api.dipsac.com/openapi.json
codegen/generate.py           writes one method per operation, for both languages
python/                       the Python package; src/dipsac/_resources.py is generated
js/                           the npm package; src/resources.ts is generated
fixtures/                     small real files the live tests upload
```

The hand-written part of each library is the transport: the key, uploads,
errors, retries, background jobs. The methods are generated from the schema, so
the two libraries cannot disagree about an endpoint.

## When the API changes

```bash
curl -s https://api.dipsac.com/openapi.json -o openapi/dipsac.openapi.json
python codegen/generate.py
```

The generator stops, with the reason, when the schema has an operation it has
not been told about: every operation needs a row in `RETURNS` saying whether it
answers with JSON or a file. The schema cannot be trusted for that (it says
"JSON" for routes that return a file), so call the new route once and read its
`Content-Type`.

Then bump the version in `python/src/dipsac/_version.py`, and in
`js/package.json` and `js/src/version.ts` together.

## Tests

```bash
# Python: unit tests against a fake transport
cd python && python -m venv .venv && .venv/bin/pip install -e ".[dev]" && .venv/bin/pytest

# JavaScript: unit tests against a local recording server (needs Node 22+ to run the tests)
cd js && npm install && npm test

# Both, against a real server
DIPSAC_BASE_URL=... DIPSAC_API_KEY=... python python/tests/live_smoke.py
DIPSAC_BASE_URL=... DIPSAC_API_KEY=... node js/tests/live_smoke.mjs
```

The live tests cover the tool API. Speech needs the GPU service, which a test
server does not have, so `client.ai` is covered by unit tests only.

## Releasing

Publishing is done by GitHub Actions with trusted publishing: no token is stored
anywhere.

- Python: push a tag `python-v<version>`, the version in `_version.py`, e.g. `python-v0.1.1`.
- npm: push a tag `js-v<version>`, the version in `package.json`, e.g. `js-v0.1.1`.

A version number can be published once, ever. Bump it before tagging.

npm holds a brand-new package behind a placeholder first. On 2026-10-08 the first
`npm publish` of this package showed a public page reading "Temporary Holding
Version", at version `0.0.0-stage`, for three minutes before `0.1.0` appeared.
That page is npm's own and is not a failed publish; `npm view dipsac version` is
what says which version is live.

## License

MIT
