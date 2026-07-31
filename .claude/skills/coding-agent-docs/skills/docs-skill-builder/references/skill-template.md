# Template for a produced `xxx-docs` skill

Fill every `<…>` from the fact sheet. Delete tier sections that do not apply. Never leave a
placeholder or an unmeasured number in the output — if a number is not in the fact sheet,
measure it or drop the claim.

## Files to emit

```
<target-path>/
├── SKILL.md                       # from the template below
├── VERSION                        # 0.1.1
├── CHANGELOG.md                   # see project convention
├── README.md                      # English overview — authoritative
├── README-cn.md                   # Chinese translation of README.md
├── scripts/
│   ├── docs_query.py              # copied verbatim from assets/docs_query.py
│   └── docs-source.json           # the site contract (below)
└── references/
    └── mechanism.md               # measured facts + decision + invalidation triggers
```

English is authoritative in every pair; when the two disagree, fix the translation. Add a
`SKILL-cn.md` only if the user asks — Claude Code loads `SKILL.md`, so a translation of it is
for human readers and is extra surface to keep in sync.

**The generated `SKILL.md` must never mention that a translation exists.** It is the published
artifact and the text that gets loaded into the agent's context; a note about translation
conventions is noise there. The convention is documented only in the translated file, which
also states that maintenance flows one way (edit the English, then sync the translation).

Omit `scripts/` entirely for **T0** — an inline-index skill needs no code.

## `docs-source.json`

```json
{
  "name": "<skill-name>",
  "index": {
    "url": "<verified index URL, post-redirect>",
    "format": "llms-txt",
    "cache_ttl_seconds": 86400
  },
  "content": {
    "mode": "plain-text",
    "url_template": "{url_no_slash}.md"
  }
}
```

Fill `index.url`, `content.mode`, and `content.url_template` from the probe's `conclusion`
(`best_index_url`, `content_mode`, `content_url_template`) rather than by hand.

- `format`: `llms-txt` or `sitemap`.
- `mode`: `plain-text` (C0/C2) or `html-webfetch` (C1). With `html-webfetch`, omit
  `url_template` unless the page URL needs rewriting; `get` then tells the agent to WebFetch.
- `url_template` placeholders: `{url}`, `{url_no_slash}`, `{path}`, `{slug}`, `{host}`.
- `content.headers`: only when the winning variant was `accept-markdown` — copy the probe's
  `conclusion.content_headers` (e.g. `{"Accept": "text/markdown"}`) and omit `url_template`.

## `SKILL.md`

````markdown
---
name: <product>-docs
description: Look up authoritative, up-to-date <Product> documentation covering <the real
  top-level areas, taken from the index's own section names>. Use when the user asks how a
  <Product> feature works, what a config field does, how to set up <top areas>, when
  troubleshooting a <Product> error, or when you need current official docs rather than
  training-cutoff knowledge.
argument-hint: [topic]
allowed-tools: <Bash(python3 *) and/or WebFetch — only what the tier actually uses>
---

# <Product> Docs

Answers <Product> questions from the official docs on demand: <one line naming the tier —
e.g. "searches a cached copy of the 202 KB llms.txt index, then fetches the matching pages
as raw markdown">. Always prefer this skill over recalling docs from memory — the docs
change faster than training data.

If the user passed an argument (`$ARGUMENTS`), treat it as the topic. Otherwise infer it.

## When to use this skill

- <area 1 — from the index's own section names>
- <area 2>
- <area 3>

Out of scope: <adjacent product/API that has its own docs, and where to send the user>.

## How this site works

Measured <YYYY-MM-DD>; full fact sheet in [references/mechanism.md](references/mechanism.md).

- **Index**: `<url>` — <bytes> B, <n> entries, <s> sections, <p>% with prose descriptions.
- **Coverage**: <n> index entries vs <m> sitemap URLs (<r>%) — <leaf-level: the index is the
  complete page list | hub-level: entries point at area landing pages, so expect a second hop>.
- **Content**: <"every page has a `.md` twin — <a> B vs <b> B of HTML" | "HTML only — use
  WebFetch, never curl the raw page">.
- **Gotchas**: <redirects, dual llms.txt, auth walls, oversized llms-full.txt — only real ones>.

## Procedure

### 1. Find candidate pages

<T0>
```
WebFetch url=<index-url>
        prompt="Return the raw markdown. I need every `- [Title](URL): description` line unmodified."
```
</T0>

<T1/T2/T3>
```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/docs_query.py search '<term>|<synonym>|<the word the docs would use>'
```
The index is fetched once and cached for 24 h, so repeat queries cost no requests. Only
matching lines enter context — never load the whole index.

Routing commands, cheapest first:

| Command | Cost | Use when |
| :--- | :--- | :--- |
| `search '<regex>'` | ~<x> tok | always start here |
| `sections` | ~<y> tok | search missed and you need the map |
| `section '<name>'` | <a>–<b> tok | full recall inside one area |
</T1/T2/T3>

### 2. If the search comes back empty

Do **not** conclude the topic is undocumented. Escalate:

1. Widen with synonyms — the docs' word is often not the user's (<a real example from this
   site, e.g. "timeout" lives under "Duration">).
2. If the query was not in English, retry with English terms. This index is English-only and
   a non-English query scores zero matches for reasons that have nothing to do with coverage.
3. `sections`, then `section '<most plausible>'` for full recall inside it.
4. <T4 only> Fetch the area landing page and follow its own links — the index lists areas,
   not every page.
5. Only then say it is not in the docs, and state what you searched.

### 3. Read the pages

<C0>
```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/docs_query.py get <url-from-search>
```
Returns raw markdown (~<n> B/page).
</C0>

<C1>
```
WebFetch url=<url-from-search>
        prompt="<the user's actual question, not 'summarize this page'>"
```
Pages are HTML-only (~<n> B raw). WebFetch converts to markdown before it reaches context —
do not curl them.
</C1>

Fetch **1–3 pages per batch**, then judge whether that answers the question. Loop if not, to
a cap of **9 pages**. At 9 and still short, stop and tell the user what you read and what is
missing — do not silently continue or fill the gap with guesses.

## Context budget

| Step | Cost | Notes |
| :--- | :--- | :--- |
| `search` | ~<x> tok | only matched lines |
| `section` | <a>–<b> tok | one area, full recall |
| page | ~<n> tok each | 1–3 per batch |

Typical question: search + 1–2 pages ≈ **<total> tokens**. Loading the index whole would be
~<index> tokens, which is why nothing here does that. Read **one** section at a time; if you
cannot tell which section to read, that is a signal to search again with better terms, not to
load several.

## Rules

- **Never invent a doc URL.** Not in the index → say so. Slugs get renamed.
- **Never load the whole index**<, and never touch `llms-full.txt` (<size>)>.
- **Cite the URL that served the content.**
- **A 404 on a page URL means the index is stale** — re-run `/docs-skill-builder check <path>`.
- **Pass through what the docs say.** The user wants current authoritative behavior, not a
  synthesis with your prior knowledge.
````

## `references/mechanism.md`

Records what was measured and what would invalidate it, so `check` can re-verify and a
future rebuild can re-decide rather than copy:

```markdown
# <product>-docs — mechanism record

Measured <YYYY-MM-DD> by `docs-skill-builder` <version>.

## Fact sheet
<paste the probe's human-readable output>

## Decision
Index tier **<T?>** because <the specific numbers that triggered it>.
Content tier **<C?>** because <same>.
Rejected: <tier> — <why, in one line>.

## What would change this decision
- <e.g. "site starts publishing per-section llms.txt → move to T1 and drop the script">
- <e.g. "prose descriptions rise above 50% → T2 becomes T1">
- <e.g. "`.md` twins appear → C1 becomes C0, big token win">

## Hand-written assets that a rebuild must preserve
- <e.g. the Chinese trigger phrases in `description` — absent from the English index and
  not reproducible by any script>
```
