---
name: codex-docs
description: Look up authoritative, up-to-date OpenAI Codex documentation covering the CLI, IDE extension, Codex app, cloud, subagents, skills, MCP, sandboxing, configuration, enterprise, and integrations. Use when the user asks how a Codex feature works, what a config field does, how to set up the CLI/IDE/app/cloud/skills/MCP, when troubleshooting a Codex error or unexpected behavior, or when you need to cite current official docs rather than rely on training-cutoff knowledge.
argument-hint: [topic or doc title]
allowed-tools: WebFetch
---

# Codex Docs

Lazy-loads the official OpenAI Codex documentation by reading the index at `https://developers.openai.com/codex/llms.txt`, picking the most relevant page(s), and fetching them on demand. Always prefer this skill over recalling docs from memory — the docs change frequently.

If the user passed an argument (`$ARGUMENTS`), treat it as the topic to look up. Otherwise infer the topic from the conversation.

## When to use this skill

Use it whenever the question is about Codex itself or anything in its docs scope:

- Codex CLI: install, slash commands, command-line options, features, configuration, sandboxing, authentication
- Codex IDE extension, Codex app (automations, commands, worktrees, computer use, Chrome extension), and Codex cloud/web
- Concepts: sandboxing, customization, subagents, skills, MCP, cyber safety
- Enterprise setup, integrations (GitHub, Linear, Slack), Amazon Bedrock, the app-server protocol, troubleshooting

If the question is about the broader **OpenAI API / OpenAI SDK** (not the Codex coding agent), that lives under `developers.openai.com/api` and is out of scope for this skill.

## Procedure

### 1. Read the index

```
WebFetch url=https://developers.openai.com/codex/llms.txt
        prompt="Return the raw markdown. I need every `- [Title](URL): description` line unmodified, including the section headers."
```

The index is a single map of ~200 lines, grouped under `## Section` headers, each entry in the form `- [Title](https://developers.openai.com/codex/<slug>.md): description`. URLs end in `.md` — every page has a Markdown twin at `/codex/<slug>.md`, so the targets are raw Markdown, not HTML.

Load the whole index in one shot and search it directly. Don't pre-filter by section header before you've seen the entries — the section grouping is just how the page is laid out, not a reason to skip parts of the map.

### 2. Pick the right page(s)

Match the user's question against the **description** (text after the colon), not just the title. Then:

- Pick **1–3 pages per batch**, not more. The index is for triage, not bulk loading.
- One specific feature ("how do Codex slash commands work?") → one page.
- Cross-concept question ("how do skills relate to subagents?") → fetch each relevant page.
- Nothing in the index obviously matches → say so. Do not guess a URL.

### 3. Fetch the batch

For each chosen URL:

```
WebFetch url=<URL from index>
        prompt="<a question that captures what the user actually needs, not 'summarize this page'>"
```

### 4. Evaluate, then loop or answer

After each batch, judge whether the fetched pages actually answer the user's question:

- **Enough** → answer, grounded in the fetched content. Cite the doc page (title + URL) when stating non-obvious facts so the user can verify.
- **Not enough** (the answer lives on a page you haven't read, or a fetched page pointed to another) → go back to step 2, pick the next 1–3 pages from the index, and fetch again.
- Keep looping until you can answer, up to a **default cap of 9 pages total** across all batches.
- **Still not enough at 9 pages** → stop. Tell the user honestly what you've read, what's still missing, and ask whether they want you to keep reading more pages. Don't silently blow past the cap or pad the answer with guesses.

## Rules

- **Never invent a doc URL.** If a page isn't in the index, it does not exist — say so instead of fabricating a slug.
- **Don't skip step 1**, even if you think you remember the right URL. Doc slugs get renamed; the index is the source of truth.
- **Loop in small batches, cap at 9 pages.** Fetch 1–3, check if that's enough, fetch more only if it isn't. If 9 pages still don't answer it, ask the user before reading more — don't grind through the whole index or fabricate the gap.
- **Stay in scope.** This skill covers `developers.openai.com/codex/*` only. For the general OpenAI API, point the user to `developers.openai.com/api`.
- **Pass through what the docs say.** Don't merge aggressively with prior knowledge — the user wants current authoritative behavior, not a synthesis.
