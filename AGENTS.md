# Odoo Agents Repository Guide

Codex reads this file before doing work in the repository.

## Repository Purpose

- This repository stores reusable skills, agents, and rules for Odoo-focused AI workflows.
- The canonical skill source lives under `skills/`.
- `.agents/skills/` is a generated mirror that exists so Codex can discover repo-scoped skills directly.

## Maintenance Rules

- Edit `skills/` only. Do not hand-edit `.agents/skills/`.
- After changing any top-level skill folder, run:
  - `node scripts/sync-codex-skills.js --write`
  - `node scripts/sync-codex-skills.js --check`
  - `npm test`
- Keep repo onboarding metadata consistent with the current GitHub repository and current flat skill paths.

## Layout

- `skills/` contains the authored skill definitions and references.
- `.agents/skills/` mirrors every top-level skill directory from `skills/`.
- `agents/` contains specialized review or helper agents.
- `rules/` contains shared standards.
- `tests/` contains repo validation.

## Odoo Frontend Routing

- Use `skills/odoo-owl/` for Owl component authoring, templates, assets, and runtime choices.
- Use `skills/odoo-webclient-extension/` for registries, client actions, services, hooks, and safe patching.
- Use `skills/odoo-owl-testing/` for HOOT, mock environments, and `web.assets_unit_tests`.
