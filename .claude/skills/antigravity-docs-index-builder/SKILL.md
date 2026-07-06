---
name: antigravity-docs-index-builder
description: Rebuild the docs-manifest.json that the antigravity-docs skill relies on, by extracting the DOCS_STRUCTURE map from the live Antigravity web app JS bundle and enriching it with titles/descriptions from llms.txt. Use when Antigravity has shipped new/renamed/removed doc pages, when antigravity-docs reports a stale or missing page, or when you simply want to refresh the manifest. Manually invoked (e.g. /antigravity-docs-index-builder).
argument-hint: [--force]
allowed-tools: Bash, Read, Write
---

# Antigravity Docs Index Builder

Regenerates `.claude/skills/coding-agent-docs/skills/antigravity-docs/references/docs-manifest.json` — the static index that the **`antigravity-docs`** skill (published as part of the `coding-agent-docs` plugin) reads to answer questions. This is a maintenance skill you run by hand whenever the Antigravity docs may have changed; `antigravity-docs` itself never runs it.

## Why this skill has to exist

Unlike Claude Code and Codex — whose doc pages have raw `.md` twins you can fetch directly — `antigravity.google/docs/*` is a **client-rendered SPA**. A plain fetch of a doc page returns an empty shell, and there is no `.md` twin at the page URL and no `llms-full.txt`. So the doc list can't be scraped by fetching pages.

But the app ships the map and the content as static resources, if you know where to look:

1. **The JS bundle** (`main-<hash>.js`) embeds a `DOCS_STRUCTURE` array of `{section, path, slug, filename}` records — the authoritative list of every doc page.
2. **The real Markdown** for each page lives at `https://antigravity.google/assets/docs/<path>/<filename>.md` (pristine, with frontmatter — this is what `antigravity-docs` fetches).
3. **`llms.txt`** lists `- [Title](/docs/<slug>): description` — human-readable titles and one-line descriptions, joinable to `DOCS_STRUCTURE` on `slug` (verified: a 1:1 join).

This builder stitches (1) + (3) into the manifest and records the content URLs from (2).

> **Critical:** the bundle must be fetched as **raw bytes** (`curl`/`urllib`), never through a markdown-converting fetcher like WebFetch — that strips `<script>` tags and the `DOCS_STRUCTURE` data with them. That's why this skill uses `Bash`, not `WebFetch`.

## Procedure

### 1. Run the builder script

```
python3 .claude/skills/antigravity-docs-index-builder/scripts/build_manifest.py
```

- Set today's date so the manifest is stamped:
  `ANTIGRAVITY_BUILD_DATE=<YYYY-MM-DD> python3 .../build_manifest.py`
- Pass `--force` (or `$ARGUMENTS`) to rebuild even when the bundle hash is unchanged.

What it does: discovers the current `main-<hash>.js` from `https://antigravity.google/docs/home`, and **short-circuits if that bundle name matches the one already recorded in the manifest** (docs structure unchanged → nothing to do). Otherwise it downloads the bundle, parses `DOCS_STRUCTURE`, fetches and joins `llms.txt`, and writes the manifest — printing the added/removed page slugs versus the previous version.

### 2. Report the result

Relay to the user: the bundle name, page count, and the added/removed diff. If pages were added or removed, that's the signal that `antigravity-docs` now covers new material (or dropped stale slugs).

### 3. If the script errors

The script fails loudly (rather than writing a bad manifest) in two cases, both meaning Antigravity changed something structural:

- **"could not find main-<hash>.js"** — the app shell markup changed. `curl -s https://antigravity.google/docs/home | grep -oE 'src="[^"]*"'` to find the new bundle-reference pattern, then update `find_bundle_name`.
- **"DOCS_STRUCTURE not found"** — the record shape changed. Download the bundle, `grep -oE '.{40}filename:"[^"]*".{20}' bundle.js` to see the new object shape, then update `parse_structure`.

Fix the script, re-run, and note what changed in this skill's `CHANGELOG.md`.

## Rules

- **Never hand-edit `docs-manifest.json`.** It is generated. Any manual fix will be silently overwritten on the next run — fix the builder instead.
- **Raw fetch only for the bundle.** WebFetch cannot see the `DOCS_STRUCTURE` data. Use `curl`/Python.
- **Verify the join.** If the script reports pages with no `llms.txt` description, that's tolerable (it falls back to a filename-derived title) but worth a glance — a large unmatched count usually means the slug scheme drifted between the bundle and `llms.txt`.
- **Don't widen scope.** This builder only writes the manifest for `antigravity-docs`. It does not fetch or cache page content — that's `antigravity-docs`' job at answer time.
