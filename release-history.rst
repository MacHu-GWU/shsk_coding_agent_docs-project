.. _release_history:

Release and Version History
==============================================================================


x.y.z (Backlog)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

**Minor Improvements**

**Bugfixes**

**Miscellaneous**


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
