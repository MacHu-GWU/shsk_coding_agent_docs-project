.. _project-overview:

Project Overview
==============================================================================

Coding agents (Claude Code, Codex, Antigravity, ...) change their commands, config formats, and workflows fast enough that anything memorized in a prompt or baked into training data goes stale quickly. This project turns each agent's official documentation into an **Agent Skill** instead: a small, reusable mechanism that looks up the current docs on demand, rather than a frozen copy of them.

On top of that foundation of grounded, current documentation, we build further skills: a knowledge base that maps the same concept (hooks, MCP servers, subagents, permissions, ...) across agents, and a family of skills that port a project's configuration from one agent to another.

Three agents are supported today: Anthropic's **Claude Code**, OpenAI's **Codex**, and Google's **Antigravity**.


What Gets Published
------------------------------------------------------------------------------
Everything under `.claude/skills/coding-agent-docs/skills/ <https://github.com/MacHu-GWU/shsk_coding_agent_docs-project/tree/main/.claude/skills/coding-agent-docs/skills>`_ is one Claude Code **plugin**, ``coding-agent-docs``, meant for external distribution. It bundles:

- Three documentation skills, one per agent — see :ref:`documentation-skills`
- A cross-agent concept-mapping knowledge base — see :ref:`concept-mapping`
- Twelve port skills that migrate a project's config between agents — see :ref:`port-skills`

This repo will eventually be referenced as one catalog entry in a separate marketplace repo, so users can install the plugin without cloning this whole project.


Maintainer-Only Tools
------------------------------------------------------------------------------
A few skills live at the top level of this repo's ``.claude/skills/`` (siblings of the ``coding-agent-docs`` plugin folder, not inside it) because they are used only to *build and maintain* the plugin's content, never shipped to plugin users:

- ``antigravity-docs-index-builder`` — regenerates the local doc manifest that ``antigravity-docs`` reads
- ``coding-agent-concept-mapping-builder`` — authors and refreshes the concept-mapping knowledge base
- ``port-coding-agent-skill-generator`` — generates the 12 port skills from two shared templates

This repo is open source, so anyone can read these tools, but installing the ``coding-agent-docs`` plugin never pulls them in — only what sits inside ``.claude/skills/coding-agent-docs/`` is part of the plugin.
