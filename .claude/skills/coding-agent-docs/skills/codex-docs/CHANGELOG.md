# Changelog

All notable changes to the `codex-docs` skill are documented here.

## [0.1.1] - 2026-07-03

- Initial release.
- Lazy-loads OpenAI Codex docs from `https://developers.openai.com/codex/llms.txt`.
- Small-batch fetch loop: 1–3 pages per batch, evaluate, continue up to a 9-page cap, then ask the user before reading more.
