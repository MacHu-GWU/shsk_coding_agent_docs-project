# Changelog

All notable changes to the `antigravity-docs-index-builder` skill are documented here.

## [0.2.1] - 2026-07-25

- Rewrote the builder for Antigravity's site rewrite: `antigravity.google/docs/*` moved from a client-rendered SPA (JS bundle + `.md` asset twins) to a server-rendered Astro app. Both of the old strategy's URLs 404 now.
- New source of truth: parses the page list from `llms.txt`'s `## Documentation` section (no more JS bundle reverse-engineering).
- New content strategy: scrapes each `/docs/<slug>` page directly for its breadcrumb section, `<h1>` title, and lead-paragraph description (capped at 280 chars) — richer than `llms.txt`'s boilerplate per-page descriptions.
- `content_url` is now the page URL itself; consumers (`antigravity-docs`) WebFetch it directly instead of a separate `/assets/docs/....md` twin.
- Change-detection short-circuit now hashes `llms.txt` content instead of the JS bundle filename.
- 77 pages at time of writing (11 new CLI pages picked up: slash commands, `cli/modes`, `cli/projects`).

## [0.1.1] - 2026-07-03

- Initial release.
- Extracts `DOCS_STRUCTURE` from the Antigravity web app JS bundle (`main-<hash>.js`) and joins titles/descriptions from `llms.txt` on `slug`.
- Writes `.claude/skills/antigravity-docs/references/docs-manifest.json` (66 pages at time of writing; bundle `main-C7HXKFZQ.js`).
- Short-circuits when the bundle hash is unchanged; `--force` to override. Prints an added/removed page diff versus the previous manifest.
