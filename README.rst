
.. image:: https://readthedocs.org/projects/shsk-coding-agent-docs/badge/?version=latest
    :target: https://shsk-coding-agent-docs.readthedocs.io/en/latest/
    :alt: Documentation Status

.. image:: https://github.com/MacHu-GWU/shsk_coding_agent_docs-project/actions/workflows/main.yml/badge.svg
    :target: https://github.com/MacHu-GWU/shsk_coding_agent_docs-project/actions?query=workflow:CI

.. image:: https://codecov.io/gh/MacHu-GWU/shsk_coding_agent_docs-project/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/MacHu-GWU/shsk_coding_agent_docs-project

.. image:: https://img.shields.io/pypi/v/shsk-coding-agent-docs.svg
    :target: https://pypi.python.org/pypi/shsk-coding-agent-docs

.. image:: https://img.shields.io/pypi/l/shsk-coding-agent-docs.svg
    :target: https://pypi.python.org/pypi/shsk-coding-agent-docs

.. image:: https://img.shields.io/pypi/pyversions/shsk-coding-agent-docs.svg
    :target: https://pypi.python.org/pypi/shsk-coding-agent-docs

.. image:: https://img.shields.io/badge/✍️_Release_History!--None.svg?style=social&logo=github
    :target: https://github.com/MacHu-GWU/shsk_coding_agent_docs-project/blob/main/release-history.rst

.. image:: https://img.shields.io/badge/⭐_Star_me_on_GitHub!--None.svg?style=social&logo=github
    :target: https://github.com/MacHu-GWU/shsk_coding_agent_docs-project

------

.. image:: https://img.shields.io/badge/Link-API-blue.svg
    :target: https://shsk-coding-agent-docs.readthedocs.io/en/latest/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Install-blue.svg
    :target: `install`_

.. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
    :target: https://github.com/MacHu-GWU/shsk_coding_agent_docs-project

.. image:: https://img.shields.io/badge/Link-Submit_Issue-blue.svg
    :target: https://github.com/MacHu-GWU/shsk_coding_agent_docs-project/issues

.. image:: https://img.shields.io/badge/Link-Request_Feature-blue.svg
    :target: https://github.com/MacHu-GWU/shsk_coding_agent_docs-project/issues

.. image:: https://img.shields.io/badge/Link-Download-blue.svg
    :target: https://pypi.org/pypi/shsk-coding-agent-docs#files


Welcome to ``shsk_coding_agent_docs`` Documentation
==============================================================================
.. image:: https://shsk-coding-agent-docs.readthedocs.io/en/latest/_static/shsk_coding_agent_docs-logo.png
    :target: https://shsk-coding-agent-docs.readthedocs.io/en/latest/

``shsk_coding_agent_docs`` distills the official documentation of coding agents into reusable Agent Skills, so an agent can pull grounded, current knowledge on demand instead of relying on stale training data. Three agents are supported today: Anthropic's Claude Code, OpenAI's Codex, and Google's Antigravity.

On top of that foundation, the project adds a knowledge base that maps the same concept (hooks, MCP servers, subagents, permissions, ...) across agents, and a family of skills that port a project's configuration from one agent to another.

Everything meant for external use ships as a single Claude Code plugin, ``coding-agent-docs``, under ``.claude/skills/coding-agent-docs/``. See the `Maintainer Guide <https://github.com/MacHu-GWU/shsk_coding_agent_docs-project/tree/main/docs/source/99-Maintainer-Guide>`_ for how the plugin is organized and maintained.


.. _install:

Install
------------------------------------------------------------------------------

``shsk_coding_agent_docs`` is released on PyPI, so all you need is to:

.. code-block:: console

    $ pip install shsk-coding-agent-docs

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade shsk-coding-agent-docs
