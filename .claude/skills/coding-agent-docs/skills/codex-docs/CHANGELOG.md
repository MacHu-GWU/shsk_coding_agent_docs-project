# Changelog

All notable changes to the `codex-docs` skill are documented here.

## [0.1.2] - 2026-07-29

- Fixed the skill, which had gone completely dark at step 1: OpenAI moved the Codex documentation body to `learn.chatgpt.com/docs/`, and the blanket 308 redirect on the old host swept up `codex/llms.txt` too, sending it to a target that does not exist (404). The new host publishes no `llms.txt` of its own.
- Switched the index to the hub-wide `https://developers.openai.com/llms.txt`, which absorbed the whole Codex map into `## Codex — <Topic>` sections in the same `- [Title](URL): description` format. Step 1 now narrows to the `## Codex —` and `## Plugins —` families, since the hub index spans several unrelated product lines.
- Documented the two-call fetch: `WebFetch` does not follow cross-host redirects, so a `developers.openai.com/codex/<slug>.md` page takes one call to learn the redirect and a second to read `learn.chatgpt.com/docs/<slug>.md`. The pair counts as one page against the 9-page cap, and the `learn.chatgpt.com` URL is the one to cite.
- Warned that the new slugs are not a straight host swap (`codex/skills.md` lands on `docs/build-skills.md`, `codex/config-reference.md` on `docs/config-file/config-reference.md`), so a `learn.chatgpt.com` URL must never be hand-assembled.
- Noted that roughly 5 of the index's 137 Codex entries are stale upstream and 404 even after the redirect; treat those as missing pages rather than repairing the slug.
- Widened scope from `developers.openai.com/codex/*` to the Codex product family across hosts, and added plugins and marketplaces (`developers.openai.com/plugins/*`, which fetch directly) to the description and the in-scope list.

## [0.1.1] - 2026-07-03

- Initial release.
- Lazy-loads OpenAI Codex docs from `https://developers.openai.com/codex/llms.txt`.
- Small-batch fetch loop: 1–3 pages per batch, evaluate, continue up to a 9-page cap, then ask the user before reading more.
