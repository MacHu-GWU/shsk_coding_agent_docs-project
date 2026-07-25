.. _release_history:

Release and Version History
==============================================================================


x.y.z (Backlog)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

**Minor Improvements**

**Bugfixes**

**Miscellaneous**


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
