.. _release_history:

Release and Version History
==============================================================================


x.y.z (Backlog)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

**Minor Improvements**

**Bugfixes**

**Miscellaneous**


0.1.4 (2026-07-31)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- Added the ``docs-skill-builder`` skill, which builds and re-verifies the ``xxx-docs`` lookup skills that this project ships. It probes a documentation site for an index (``llms.txt``, ``.well-known/llms.txt``, sitemap) and for a plain-text content contract, measures what it finds, and picks the cheapest lazy-load design from a tiered catalog rather than guessing. Ships ``probe_docs_source.py`` (a throttled, budgeted prober that tests six plain-text content conventions against a real page and calibrates against a deliberately bogus URL, so soft 404s and auth walls do not read as success), a reusable ``docs_query.py`` for the tiers that need a query script, a mechanism catalog with the decision tables, and an output template. Also covers ``check`` mode for auditing an existing skill against its recorded baseline.
- ``docs-skill-builder`` now requires every skill it produces to keep an append-only ``references/mechanism.md`` log — newest entry on top, past entries never rewritten — so a later audit can see what was believed at the time and why it changed, instead of only the current conclusion. Every build and every check appends one entry, including checks that found nothing, because a check that leaves no trace is indistinguishable from a check that never ran. Entries carry word budgets scaled to how much actually moved. Produced skills must also ship three translated pairs (``SKILL.md``, ``README.md``, ``references/mechanism.md`` each with a ``-cn.md`` counterpart), with English authoritative and both halves updated in the same pass.

**Minor Improvements**

- Refreshed ``claude-code-docs`` against fresh measurements and gave it a recall-escalation ladder. Two rules were missing and both were added off measured evidence: a translate-first rule (the Chinese query ``钩子`` matches 0 of the 174 index entries where ``hook`` matches 17, so a non-English miss said nothing about coverage) and a synonym-widening step (``resume`` appears in 0 titles but 5 descriptions, under *Manage sessions*). Also added the measured page-size spread (10,628 B to 272,484 B, a 25x range) as a reason to send ``WebFetch`` a pointed question, a guard against the 6.5 MB ``llms-full.txt`` sitting one path from the index, and a note that index URLs already end in ``.md`` and must be used verbatim. The stale "~150 entries" claim is now 174, and the description was broadened to cover doc areas that shipped since the last release (agent teams, workflows, worktrees, channels, routines, scheduled tasks, sandboxing, code review, and the desktop/web/mobile/Slack/Chrome surfaces).
- Brought all three ``xxx-docs`` skills up to the current output spec: ``claude-code-docs``, ``codex-docs``, and ``antigravity-docs`` now each ship a mechanism log and the three translated pairs. The ``codex-docs`` and ``antigravity-docs`` logs are marked as reconstructions rather than measurements — they were recovered from the shipped skills without re-probing, and say so, so the next real check knows it is establishing the first measured baseline. Recording ``codex-docs``' design also surfaced a tier decision it had been implementing without stating: routing by the vendor's own ``## Codex —`` and ``## Plugins —`` sections, because the hub index is mostly unrelated product lines.

**Bugfixes**

- Fixed the ``antigravity-docs`` manifest, whose description column had silently degraded to ``llms.txt`` boilerplate. ``antigravity-docs-index-builder`` scraped each page's lead paragraph from a ``template-content-paragraph`` class that no longer exists anywhere in the site's HTML, so all 81 pages fell back to "Learn about X" — leaving triage running on title and breadcrumb alone. The selector is now the first substantial ``<p>`` after the body's ``<h1>``. Regenerating the manifest took boilerplate descriptions from 81/81 to 0/81 and median description length from 3 words to 21. Measured against the old manifest on queries whose words appear in no title and no breadcrumb: ``isolation`` 0 to 1 match, ``parallel`` 0 to 2, ``open standard`` 0 to 6.
- Made that class of failure impossible to miss. The builder only ever counted network exceptions as scrape failures, so a selector that matched nothing degraded every page while the build reported success — which is why the above went unnoticed for five days. Every run now prints a scrape-coverage block per field, and a field that falls back on more than half the pages that fetched fine gets a prominent warning naming the regex to check. Pages that failed to fetch are discounted first, so a 404 is not misreported as a broken selector.
- Fixed two text-extraction defects in the same builder: stripped tags are now replaced with a space rather than deleted (``/docs/enterprise`` had been producing "Antigravity 2.0Antigravity CLI"), and extracted text is HTML-unescaped, so titles and breadcrumbs no longer carry raw entities such as "Background tasks &amp;amp; subagents".
- Fixed unparseable YAML frontmatter in ``docs-skill-builder``, which blocked plugin validation for this release. Its ``argument-hint`` began with ``[build|check]``, and a YAML value starting with ``[`` is a flow sequence rather than a string — the brackets closed early and the rest of the line became an unanchored scalar, so the whole document failed to parse. The value is now quoted. This is worth more than a one-line fix because of how it presents: a skill whose frontmatter fails to parse does not error, it loads with **empty metadata** — no name, no description — and therefore silently never triggers. The reported parse error also points at line 2 rather than the offending line. So ``docs-skill-builder`` now specifies quoting in its output template and, more importantly, opens its acceptance test by parsing the emitted frontmatter and asserting four string fields, before any lookup test runs against a skill the agent might no longer be able to find. Every ``SKILL.md`` in the repository was re-parsed; this was the only broken one.


0.1.3 (2026-07-29)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- Added the ``plugins-and-marketplaces`` concept (09) to the ``coding-agent-concept-mapping`` knowledge base, covering the plugin package and manifest, bundled component types, marketplace catalogs and source types, and install location, scope, and enablement. Claude Code and Codex turn out to align almost exactly (``.claude-plugin`` / ``.codex-plugin`` manifests, a ``marketplace.json`` catalog, the same relative-path / git / ``git-subdir`` / ``npm`` source types, a matching ``plugin marketplace add`` command); Antigravity has plugins but no marketplace of any kind, and its manifest schema is ``name`` plus ``description`` with ``additionalProperties: false``.

**Bugfixes**

- Fixed the ``codex-docs`` skill, which had gone dark at its very first step: OpenAI moved the Codex documentation body to ``learn.chatgpt.com/docs/``, and the blanket 308 redirect left on the old host swept up ``codex/llms.txt`` too, sending it to a target that does not exist on the new host. The index is now the hub-wide ``developers.openai.com/llms.txt``, which absorbed the Codex map into ``## Codex — <Topic>`` sections. The skill also now documents the two-call fetch (``WebFetch`` does not follow cross-host redirects), warns that the new slugs are not a straight host swap so a ``learn.chatgpt.com`` URL must never be hand-assembled, and notes that ~5 of the index's 137 Codex entries are stale upstream. Scope widened from ``developers.openai.com/codex/*`` to the Codex product family across hosts, including the ``developers.openai.com/plugins/*`` builder pages.
- Refreshed concepts 01 through 08 of ``coding-agent-concept-mapping`` against current docs. The Antigravity column of ``07-subagents.md`` was substantially rewritten: Antigravity now ships a full file-based subagent spec (``.agents/agents/<name>.md``, Markdown with YAML frontmatter, body as system prompt) that mirrors Claude Code, resolving five cells that previously read ``unconfirmed`` or ``No equivalent``. MCP scope precedence in ``06-mcp-servers.md`` was resolved from ``unconfirmed`` using the new ``cli/mcp`` page.
- Replaced every dead source URL across the knowledge base: Antigravity ``assets/docs/....md`` links (all 404 since the SSR rewrite) now point at the doc pages, and Codex ``developers.openai.com/codex/*.md`` links now point at their ``learn.chatgpt.com/docs/*`` destinations. All 51 source URLs verified reachable.

**Minor Improvements**

- Refreshed the ``antigravity-docs`` manifest to 81 pages (up from 77), adding ``cli/mcp``, ``ide/mcp``, ``sdk/mcp``, and ``cli/headless``.
- Updated the concept-mapping standard's sourcing rules to describe the current URL landscape for all three tools, and reserved registry number 09.
- Repointed ``coding-agent-concept-mapping-builder`` at the real knowledge-base location. Every path it wrote to still said ``.claude/skills/coding-agent-concept-mapping/``, a directory that no longer exists since the knowledge base moved into the ``coding-agent-docs`` plugin at ``.claude/skills/coding-agent-docs/skills/coding-agent-concept-mapping/``. Fixed 8 occurrences across the skill body, the standard, the concept-file template, and the example prompt.
- Replaced the generated files' maintenance pointer to the builder with an absolute GitHub URL. A relative path could never work there: the knowledge base ships inside the plugin and the builder, a maintainer-side tool, does not. Added a rule to the builder and its standard so regenerated files keep using the absolute form and say the builder is not shipped.


0.1.2 (2026-07-25)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Minor Improvements**

- Added the ``maintain-claude-plugins`` skill, with ``mise run list-plugins`` / ``mise run tag-plugin`` tasks and a ``plugin_release.py`` CLI, to validate and tag Claude Code plugin releases.

**Bugfixes**

- Fixed the ``antigravity-docs`` skill, which had gone completely dark: Google Antigravity rewrote its docs site from a client-rendered SPA to a server-rendered app, and every ``content_url`` in the manifest (previously pointing at a ``/assets/docs/....md`` twin) started returning 404. ``antigravity-docs-index-builder`` now builds its page list from ``llms.txt`` and scrapes each live doc page directly for its breadcrumb section, title, and a real lead-paragraph description, and ``content_url`` now points at the doc page itself. The manifest has been refreshed to 77 pages (up from 66).

**Miscellaneous**

- Updated the project description in ``pyproject.toml`` to accurately describe what this project does.
- Updated ``README.rst``: temporarily disabled the CI / Codecov / PyPI badges (not yet applicable to this project) and fixed the plugin directory link.
- Refreshed the project logo and favicon.


0.1.1 (1970-01-01)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- First release
