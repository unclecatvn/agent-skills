# Odoo project rules

<!-- Merge into the project's CLAUDE.md (and AGENTS.md for other agents). Adjust version and layout. -->

Odoo version: **18.0**. Addons roots, in `addons_path` order: `erp`, `erp-external`,
`erp-internal` (Enterprise). Each is its own git repository.

Machine-local runtime lives in `.claude/odoo.json` (gitignored), read by the `odoo-workflow`
helper:

```json
{"odoo_version": "18.0", "odoo_root": "/path/to/odoo/18.0", "conf": "/path/to/odoo/18.0/odoo.conf",
 "python": "/path/to/odoo/18.0/.venv/bin/python3", "dev_db": "v18_dev"}
```

## Every Odoo change

- Run the `odoo-workflow` skill first - before brainstorming or planning skills, which start
  from its Context Brief - then the Odoo 18 pack for the guide you need.
  No code without a Context Brief that cites `file:line` in the real source.
- Throwaway databases only (`scratch_*`, `upg_*`). Never install or upgrade modules on
  `v18_dev`, staging, or a customer copy unless asked by name.
- Stored-field renames, removals, and type or selection-key changes ship with a manifest version
  bump and a `migrations/<version>/` script.
- Bind `sudo()` results to `<name>_sudo`; never return them from public methods.
- Strings changed: regenerate `i18n/<module>.pot` and merge every `.po` (file names unchanged)
  before commit.

## Never

- `ponytail:` or "simplified for now" comments in this repo.
- `Co-Authored-By`, `Generated with`, or session links in commits or PR bodies.
  Disable them at the source once with the Claude Code `attribution` setting
  (`{"commit": "", "pr": ""}`, project or user level - see the agent-skills README).

## Commits

- Use the `odoo-commit` skill: `[TAG] module: description`, one module per commit, one commit
  and PR per repository.
