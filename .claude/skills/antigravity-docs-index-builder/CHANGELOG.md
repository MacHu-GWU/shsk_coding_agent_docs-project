# Changelog

All notable changes to the `antigravity-docs-index-builder` skill are documented here.

## [0.1.1] - 2026-07-03

- Initial release.
- Extracts `DOCS_STRUCTURE` from the Antigravity web app JS bundle (`main-<hash>.js`) and joins titles/descriptions from `llms.txt` on `slug`.
- Writes `.claude/skills/antigravity-docs/references/docs-manifest.json` (66 pages at time of writing; bundle `main-C7HXKFZQ.js`).
- Short-circuits when the bundle hash is unchanged; `--force` to override. Prints an added/removed page diff versus the previous manifest.
