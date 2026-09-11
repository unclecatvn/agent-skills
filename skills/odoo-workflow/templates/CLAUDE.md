# Odoo project rules

<!-- Paste into the project's CLAUDE.md. Adjust the version and the addons path. -->

Odoo version: **18.0** (also pinned in `.odoo-version`). Custom addons live in `addons_customs/`.

## Every Odoo change

- Run the `odoo-workflow` skill first, then the `odoo-18` skill for the guide you need.
  No code without a Context Brief that cites `file:line` in the real source.
- Bind `sudo()` results to `<name>_sudo`; never return them from public methods.
- Strings changed: regenerate `i18n/<module>.pot` and merge every `.po` before commit.

## Never

- `ponytail:` or "simplified for now" comments in this repo.
- `Co-Authored-By`, `Generated with`, or session links in commits or PR bodies.
  Disable them at the source once with the Claude Code `attribution` setting
  (`{"commit": "", "pr": ""}`, project or user level - see the agent-skills README).

## Commits

- Use the `odoo-commit` skill: `[TAG] module: description`, one module per commit.
