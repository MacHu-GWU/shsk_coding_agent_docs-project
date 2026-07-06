.. _documentation-skills:

Documentation Skills
==============================================================================

Three skills, one per agent: ``antigravity-docs``, ``claude-code-docs``, and ``codex-docs``. Loading one is equivalent to having on-demand access to that agent's whole documentation set.

What matters isn't that a skill copies doc content into a file — it's that each one encodes *how that agent's doc index is organized*, so the skill can always fetch the current page rather than a frozen snapshot. Every agent lays its docs out differently, so each skill's mechanism is designed on its own terms; no single template fits all three.

All three follow the same **lazy-loading, agentic-search** loop: read an index, match the user's question against it, fetch only the 1-3 pages that look relevant, and loop (capped) if that isn't enough. This keeps context usage low while guaranteeing the answer is grounded in the current docs.


Where Each Index Comes From
------------------------------------------------------------------------------
- ``claude-code-docs`` and ``codex-docs`` fetch a live ``llms.txt`` index at query time — both agents publish raw ``.md`` twins at their doc URLs, so no local caching is needed.
- ``antigravity-docs`` is different: Antigravity's doc pages are a client-rendered SPA with no fetchable ``.md`` twin. So it reads a **local manifest** (``references/docs-manifest.json``) instead, and fetches each page's separate content URL found in that manifest.


The Companion Index Builder
------------------------------------------------------------------------------
Because ``antigravity-docs`` depends on a local manifest, it has a companion maintainer-only skill: ``antigravity-docs-index-builder`` (see :ref:`project-overview`). Its only job is regenerating that manifest when Antigravity ships new, renamed, or removed pages — it plays no part in day-to-day lookups, and ``antigravity-docs`` itself never runs it.
