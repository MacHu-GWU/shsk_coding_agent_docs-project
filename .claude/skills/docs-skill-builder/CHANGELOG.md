# Changelog

All notable changes to the `docs-skill-builder` skill are documented here.

## [0.1.1] - 2026-07-30

- Initial release. Builds (and re-verifies) `xxx-docs` lazy-loading documentation skills from
  a measured probe of the target site, rather than from assumptions about its layout.
- `scripts/probe_docs_source.py` — bounded (~28 requests), throttled, stdlib-only probe. Emits
  a fact sheet covering index candidates, index structure and description coverage, the
  plain-text content contract, sitemap size, and robots. Everything the decision needs is a
  measured number.
  - Calibrates against a deliberately bogus URL, so sites that answer `200` for missing paths
    are classified correctly. Verified against `docs.databricks.com`, whose 404 is a
    consistent 12,999-byte `text/html` body.
  - Rejects auth walls: a `200` served from `/login?next=…` is not evidence a file exists
    (observed on `vercel.com/llms-full.txt`).
  - Reports **index coverage** — index entries vs sitemap URLs. Databricks lists 252 entries
    against 5,645 sitemap URLs (4.5%), which identifies its `llms.txt` as a curated hub index
    and forces a second-hop design that entry counts alone would have hidden.
  - Tests six content conventions (`.md`, `/index.md`, `.txt`, `Accept: text/markdown`,
    `?plain=1`, as-is) against a real leaf page on the docs host.
- `assets/docs_query.py` — the runtime copied verbatim into each produced skill, driven by a
  per-site `docs-source.json` so the spec lives in data and not in forked code. Supports
  `search` / `sections` / `section` / `get` / `stats` / `refresh` over `llms-txt` or `sitemap`
  indexes; filtering happens outside the model's context, so cost tracks matches rather than
  index size. Caches the index under `~/.cache/claude-docs-skills/` with a 24 h TTL, making
  repeat queries cost zero requests, and falls back to a stale cache when the network fails.
- `references/mechanism-catalog.md` — the decision tables: six index tiers (T0 inline → T5
  pre-built manifest) and three content tiers, each keyed to a probe number; the recall ladder;
  the levels-vs-recall tradeoff; the conditions that justify crawling; and the acceptance test.
- `references/skill-template.md` — file set, `docs-source.json` schema, and the SKILL.md
  skeleton for produced skills, including the mandatory context-budget table.
- Measured worked examples baked into the catalog: Vercel (202 KB index, 86% bare
  descriptions, `.md` twin at 4,991 B vs 916,562 B of HTML — 99% cheaper) and Databricks
  (47 KB index, 98% prose, HTML-only content at 50,782 B/page).
