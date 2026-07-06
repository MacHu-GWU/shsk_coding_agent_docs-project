.. _port-skills:

Port Skills
==============================================================================

With the documentation skills and the concept-mapping knowledge base in place, the last piece is migration: taking one agent's configuration in a project and porting it to another agent.

For every ordered pair of agents there are two skills: ``port-<source>-to-<target>``, which performs the migration, and ``port-<source>-to-<target>-checker``, which does a read-only audit of how complete a migration is and writes a gap report to the project's ``tmp/review-port-<source>-to-<target>.md``. With three agents convertible pairwise in both directions, that's 6 directions, 2 skills each, 12 skills total.

Neither skill hardcodes the list of portable concepts (project prompt, settings, skills, hooks, MCP servers, subagents, permissions, ...). Every run, they read the roster fresh from the ``coding-agent-concept-mapping`` index, so a newly mapped concept is picked up automatically without touching any of the 12 skills.


The Generator
------------------------------------------------------------------------------
These 12 skills are never hand-written — they're manufactured by the maintainer-only ``port-coding-agent-skill-generator`` (see :ref:`project-overview`) from two shared templates, one for the port skill and one for the checker. Running it with a direction (for example ``cc to cdx``, or spelled out as "claude code to codex") plugs the source/target agents into both templates and (re)writes the pair's ``SKILL.md`` files.

The list of agents *is* hardcoded in the generator, since adding a fourth agent is rare and the lookup table (canonical name, slug, docs skill) is small and stable. To change how all port skills behave, edit the templates and regenerate — never hand-edit a generated file.
