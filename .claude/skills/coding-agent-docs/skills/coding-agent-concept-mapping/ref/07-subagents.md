# Subagents

A subagent is a delegated agent with its own system prompt, tool set, and isolated context, spawned to handle a focused task without cluttering the main conversation. All three tools have the concept and all isolate the subagent's context, but they differ on how a subagent is defined, whether the main agent delegates to it on its own, and how much a subagent can be tailored. Claude Code is the most configurable, Codex is explicit only, and Antigravity leans on runtime definition and background parallelism.

## 1. Definition file and format

A subagent needs its definition somewhere. Claude Code and Codex each use one file per agent in different formats, while Antigravity either bundles agents in a plugin or defines them at run time with no file at all.

| Dimension | Claude Code | Codex | Antigravity |
|---|---|---|---|
| File | `.claude/agents/<name>.md` | `.codex/agents/<name>.toml` | a plugin's `agents/` folder, or no file |
| Format | Markdown, and the body is the system prompt | TOML | file format unconfirmed; also a runtime `define_subagent` tool |
| Scope | project and user, plus plugin and managed | user `~/.codex/agents/` and project `.codex/agents/` | global plugin bundle; a workspace file is unconfirmed |
| Porting-in notes | put the system prompt in the Markdown body and the config in YAML frontmatter | rewrite a Markdown agent as TOML, with the prompt in `developer_instructions` | there is no standalone project file, so bundle the agent in a plugin or define it at run time with `define_subagent` |

---

## 2. Config fields

The fields that shape a subagent decide how tightly it can be specialized. Claude Code exposes the largest set, Codex a compact one, and Antigravity documents only coarse choices.

| Dimension | Claude Code | Codex | Antigravity |
|---|---|---|---|
| Identity | `name` and `description` | `name` and `description` | `name` and `description` unconfirmed for file defined agents |
| System prompt | the Markdown body | `developer_instructions` | a custom system prompt through `define_subagent` |
| Tool access | `tools` allow list and `disallowedTools` deny list | `sandbox_mode` and `mcp_servers` | coarse toolsets: read only, write, or delegation |
| Model | `model`, defaulting to `inherit` | `model` and `model_reasoning_effort` | No equivalent; it uses the parent model |
| Porting-in notes | a rich frontmatter set also covers permissions, memory, hooks, and more | tool access is a sandbox mode and MCP list, not a per tool allow list | a subagent picks a broad toolset tier rather than naming tools, and cannot choose its own model |

---

## 3. Invocation

Whether the main agent reaches for a subagent on its own, or only when told, is the sharpest behavioral split. Each tool also ships a small set of built in agent types.

| Dimension | Claude Code | Codex | Antigravity |
|---|---|---|---|
| Automatic delegation | yes, driven by the `description` | no, explicit only | yes, the primary agent delegates to parallel subagents |
| Explicit trigger | name it, `@agent-<name>`, or `claude --agent` | a direct instruction to spawn | the `invoke_subagent` tool |
| Built in types | `Explore`, `Plan`, `general-purpose` | `default`, `worker`, `explorer` | `research`, `browser`, `self` |
| Porting-in notes | add "use proactively" to the `description` to encourage automatic delegation | nothing runs a subagent unless you ask, so name it in the instruction | delegation happens automatically through the async architecture, and a parent can also call `invoke_subagent` |

---

## 4. Context and tool isolation

Every tool runs a subagent in its own context and returns only a summary, so the main conversation stays clean. They differ on how a subagent's permissions relate to the parent's.

| Dimension | Claude Code | Codex | Antigravity |
|---|---|---|---|
| Context | a fresh window with no conversation history; only a summary returns | fresh context, only summaries return | a clean slate, with results sent back to the parent |
| Tool ceiling | bounded by `tools` and the permission settings | inherits the parent sandbox, overridable per agent | cannot exceed what the parent has already approved |
| Escalation | a subagent can be granted its own MCP servers and hooks | a subagent can narrow but not widen host keys | a subagent can never escalate beyond the parent |
| Porting-in notes | give a subagent its own `mcpServers`, `hooks`, or `memory` when it needs them | a subagent reapplies the parent's runtime overrides and cannot loosen them | a subagent inherits the parent's approvals and still prompts for anything unapproved |

---

## 5. Parallelism and management

Running several subagents at once is where these systems converge in spirit but differ in controls. Claude Code and Antigravity both foreground background execution with a manager, while Codex exposes numeric caps.

| Dimension | Claude Code | Codex | Antigravity |
|---|---|---|---|
| Parallel and background | subagents run in background by default and in parallel | parallel by default, capped by `agents.max_threads` | background parallel threads are the headline model |
| Nesting | a subagent can spawn others, up to depth 5 | `agents.max_depth`, default 1 | the delegation toolset lets an agent spawn others |
| Manager command | `/agents` prints where definitions live | no dedicated manager command | `/agents` opens the Agent Manager panel |
| Porting-in notes | `/tasks` and the @-mention typeahead track running background subagents | raise `agents.max_threads` for concurrency and `agents.max_depth` to allow nesting | the Agent Manager panel monitors every active, completed, or failed subagent |

---

## 6. Sources

**Claude Code**

- Create custom subagents: https://code.claude.com/docs/en/sub-agents.md
- Run agents in parallel: https://code.claude.com/docs/en/agents.md

**Codex**

- Subagents: https://developers.openai.com/codex/subagents.md
- Subagents concept: https://developers.openai.com/codex/concepts/subagents.md

**Antigravity**

- CLI Subagents: https://antigravity.google/assets/docs/cli/cli-subagents.md
- Subagents: https://antigravity.google/assets/docs/antigravity-2-0/subagents.md
- CLI Plugins: https://antigravity.google/assets/docs/cli/cli-plugins.md
