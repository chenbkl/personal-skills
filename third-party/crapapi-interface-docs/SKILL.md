---
name: crapapi-interface-docs
description: Query the internal CrapAPI documentation platform by API URL and return authoritative interface metadata, request headers, input parameters, hierarchical response parameters, examples, and error codes. Use when the user asks to 查接口文档、根据接口地址核对入参出参、dump/save CrapAPI 文档、or verify fields for a /debapi/ endpoint.
---

# CrapAPI Interface Docs

Use the bundled deterministic query script first. It reads public, read-only endpoints and does not require or store login credentials.

## Query

Run from this skill directory:

```bash
python3 scripts/query_interface_docs.py "/debapi/withhold/individual/zfbSign"
```

Pass multiple URLs in one call when the user supplies several interfaces. Use `--format json` only when raw structured output is needed; Markdown is the default.

The script must:

- normalize full URLs and relative `/debapi/` paths;
- restrict results to project `156939461626807001127`;
- fetch candidate details and require exact `fullUrl` equality;
- preserve response hierarchy from each field's `deep` value;
- fail without guessing when no exact match or multiple exact matches exist.

## Respond or dump

- By default, summarize the Markdown result directly in chat, emphasizing method, input parameters, response parameters, status values, and discrepancies relevant to the user's code.
- When the user explicitly asks to dump/save, generate Markdown on stdout, then use `apply_patch` to create `接口文档-<接口名>.md` in the requested/current workspace. Do not overwrite an existing file without first comparing it.
- Treat the platform response as the source of truth. Clearly label any inference or suspected documentation typo.

## Browser fallback

If the HTTP script fails because the public endpoints are unavailable, read [references/platform.md](references/platform.md), then use the available Browser skill to follow the documented UI path. Rely on the user's existing browser/Tampermonkey login state; never read, request, or persist credentials inside this skill.

## Manual-login userscript

The optional Tampermonkey template and generator support manual browsing:

```bash
cp .env.example .env
python3 scripts/generate_crapapi_login_userscript.py
```

Keep `.env` and `*.generated.user.js` local and uncommitted. Never print their credential contents.
