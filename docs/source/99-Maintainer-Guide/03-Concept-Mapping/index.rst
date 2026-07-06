.. _concept-mapping:

Concept Mapping
==============================================================================

With three documentation skills in place, one question remains: how does the same concept show up across different agents? That's what the ``coding-agent-concept-mapping`` skill answers.

For a given concept — hooks, MCP servers, subagents, permissions, and so on — it reads the official docs for all three agents and writes a side-by-side mapping of how that concept is named, configured, and behaves in each one, or notes that an agent has no equivalent. Claude Code's terminology is the baseline; the other two columns describe how they implement the same idea. The value isn't three separate glossaries, it's the alignment between them, plus a heads-up on the pitfalls of porting a config from one tool to another.

This gives a simple routing rule: a question specific to one agent goes to that agent's documentation skill; a question about how a shared concept maps across agents goes to ``coding-agent-concept-mapping``.


The Companion Builder
------------------------------------------------------------------------------
Like the documentation skills, this knowledge base has a maintainer-only companion: ``coding-agent-concept-mapping-builder`` (see :ref:`project-overview`). It reads the three documentation skills and grounds every conclusion in the official docs, never memory. It's the tool that adds a new concept, refreshes one against current docs, or rolls the per-concept files up into the index — ``coding-agent-concept-mapping`` itself stays read-only at query time.
