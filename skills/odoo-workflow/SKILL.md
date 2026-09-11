---
name: odoo-workflow
description: >
  Mandatory pre-code gate and definition-of-done for ANY Odoo change (add field, override method,
  inherit view/xpath, wizard, cron, controller, report, security, bug fix, refactor, "optimize",
  "clean code", "stick to base"), Odoo 16-19. Run BEFORE brainstorming or planning: Odoo design
  questions are answered by tracing the real source into a Context Brief (file:line), not by
  open-ended Q&A. Resolves the Odoo version, loads the matching odoo-<major> pack, and closes
  with the i18n / security / hygiene checklist before commit.
globs: "**/*.{py,xml,csv,js,ts,css,scss}"
---

# Odoo Workflow - trace first, then code

Procedure for every Odoo change. The expensive failures are always the same: a field or
method that does not exist in the base addon, an xpath anchor that was never there, a
`sudo()` nobody can audit, a `.pot` that was never regenerated. The fix is mechanical:
**no citation, no code**.

## When this applies

- Any request that ends in Odoo Python or XML: new field, override, inherited view, wizard,
  cron, controller, report, security, bug fix, refactor, "optimize", "clean up".
- Skip for pure questions, documentation-only changes, and git-only tasks (use `odoo-commit`).
- Generic brainstorming/planning skills come *after* Step 2, and only if the business intent
  is still unclear - the Context Brief is the input they need.

## Step 0 - Resolve the Odoo version, load the pack

Resolve `ODOO_VERSION` in this order and stop at the first hit:

1. Explicit statement from the user or the project `CLAUDE.md`.
2. `.odoo-version` at the repo root, `odoo_version` in `.claude/odoo.json`,
   `odoo.version` in `package.json`, `tool.odoo.version` in `pyproject.toml`.
3. Dominant `'version'` major across workspace `__manifest__.py` files.
4. Nothing found: ask once, then offer to write `.odoo-version` so it is never asked again.
   Do not silently assume a version.

Then load the `odoo-<major>` skill (`odoo-16` ... `odoo-19`) and read only the guide the task
needs from its `references/`. If the pack is not installed, say so and continue with the trace
below - the real source is the authority; never fill the gap from memory.

## Step 1 - Trace the chain (grep first, read ranges)

Resolve `ROOTS` once: `addons_path` from `*.conf` / `docker-compose*.yml` / `.claude/odoo.json`;
otherwise `find . -maxdepth 4 -name __manifest__.py -exec dirname {} \; | xargs -n1 dirname | sort -u`.
Core (`odoo/addons`), enterprise, and custom addons are all roots.

For every model `MODEL`, method `METHOD`, field `FIELD`, or view the task touches
(replace the uppercase placeholders):

| Need | Command |
|------|---------|
| Model definition | `grep -rnE --include=*.py "_name\s*=\s*['\"]MODEL['\"]" $ROOTS` |
| Every extension | `grep -rnE --include=*.py "_inherit\s*=.*['\"]MODEL['\"]" $ROOTS` |
| Super chain of a method | `grep -rnE --include=*.py "def METHOD\(" <model files>` - order by each module's `depends` (load order = MRO) |
| Field definition | `grep -rnE --include=*.py "^\s+FIELD\s*=\s*fields\." <model files>` |
| Views on the model | `grep -rlE --include=*.xml "<field name=\"model\">MODEL</field>" $ROOTS` |
| Existing inherits of a view | `grep -rn --include=*.xml "inherit_id=\"module.view_id\"" $ROOTS` - xpath collision check |
| Xpath anchors | `grep -nE "name=\"FIELD\"\|<notebook\|<page \|<group \|<header" <view file>` |
| ACL / record rules (`MODEL` with `.` → `_`) | `grep -rn --include=ir.model.access.csv "model_MODEL," $ROOTS`; `grep -rln --include=*.xml "model_MODEL\"" $ROOTS \| grep security` |
| Tests to mirror | `ls <base module>/tests/`; `grep -rnE "def test_.*METHOD" <module>/tests` |
| JS (only if touched) | `grep -rnE --include=*.js "patch\(\|registry\.category\(" <module>/static` |

Reading budget - this is where tokens go:

- Read ranges, not files: `sed -n 'A,Bp'` or Read with offset/limit, at most 120 lines per hop.
- At most 3 hops inline. Deeper or cross-module flows go to the `odoo-code-tracer` agent with
  `odoo_version` set **if it is installed**; otherwise keep going with the table above.
- Never re-read a file already cited in the Brief.

## Step 2 - Context Brief (no citation, no code)

Write the brief before any code, at most 15 rows:

| Layer | Symbol | Source (file:line) | Base behaviour | Change |
|-------|--------|--------------------|----------------|--------|
| model | `sale.order` | `addons/sale/models/sale_order.py:41` | `_name`, inherits `mail.thread` | inherit |
| method+super | `action_confirm` | `...sale_order.py:1012`; override `sale_stock/models/sale_order.py:88` | sets state, creates pickings | call super, then X |
| view+xpath | `sale.view_order_form` | `addons/sale/views/sale_order_views.xml:210`, anchor `partner_id` | - | add field after anchor |

Fixed layers: model / field / method+super / view+xpath / security / data / i18n / test.

Rules:

- An empty **Source** cell means no code for that row. This includes xpath anchors, group
  xmlids in `ir.model.access.csv`, and `depends` entries. Write "not found in base - drop or ask".
- Reuse over invent: before adding a field, helper, or compute, grep for an existing one.
- "Optimize" / "clean code" means: follow the base implementation's pattern with the minimal
  delta. It never means rewriting what `super()` already does.

## Step 3 - Minimal plan

At most 10 bullets: files to touch, files explicitly not touched, what is deferred. One module
unless the Brief proves the change belongs to two. YAGNI: no config for a value that never
changes, no helper used once, no abstraction with one implementation.

## Step 4 - Implement

- Apply the pack's `Coding Conventions` for the guide you opened; existing stable-addon style
  wins over personal preference.
- Overrides call `super()` and add the smallest delta; never copy the base body.
- `sudo()` naming: bind any recordset obtained through `sudo()` to a name ending in `_sudo`
  (`partner_sudo = self.partner_id.sudo()`,
  `orders_sudo = self.env['sale.order'].sudo().search(domain)`). A one-shot call
  (`record.sudo().write(vals)`) needs no variable. Never return a `_sudo` recordset from a
  public method or keep it on `self`.
- No `ponytail:` or other "simplified for now" markers in Odoo code - either the code is right
  or the plan in Step 3 says what was deferred.
- New user-facing strings go through `_()` / `_t()` / `string=` / `help=` so they are extractable.

## Step 5 - Definition of done

- [ ] Tests written for the change and run:
      `odoo-bin -c <conf> -d <db> -u <module> --test-enable --test-tags /<module> --stop-after-init`.
- [ ] `ir.model.access.csv` rows for every new model; record rules where the base model has them.
- [ ] **i18n** - whenever a string changed (`_()`, `_t()`, `string=`, `help=`, selection label,
      report text). Update the module first so the new terms are in the database, then export
      by version:
  - Odoo 16-18: `odoo-bin -c <conf> -d <db> -u <module> --stop-after-init`, then
    `odoo-bin -c <conf> -d <db> --i18n-export=<addons>/<module>/i18n/<module>.pot --modules=<module>`
    (`--modules` is required - the output path does not restrict the export scope).
  - Odoo 19: `odoo-bin i18n export -c <conf> -d <db> <module>` writes `<module>/i18n/<module>.pot`;
    `odoo-bin i18n export -c <conf> -d <db> -l vi_VN <module>` writes the `.po`.
  - Then refresh every shipped locale: `msgmerge --update i18n/<lang>.po i18n/<module>.pot`.
- [ ] **Hygiene** - only added lines are checked, so deleting a forbidden line never trips it:

  ```bash
  git diff HEAD -U0 | grep -E '^\+[^+]' | grep -nE 'ponytail:|Co-Authored-By|Generated with'
  git ls-files --others --exclude-standard | xargs -r grep -nE 'ponytail:|Co-Authored-By|Generated with'
  ```

  Both must print nothing. Before opening a PR also check the commits and the PR body:
  `git log <base>..HEAD --format=%B | grep -nE 'Co-Authored-By|Generated with'`.
- [ ] Commit through `odoo-commit` (`[TAG] module: description`, no AI attribution). The PR body
      explains WHY plus test evidence; no generated-with footer.

## Step 6 - Hand off

Run the `odoo-code-review` agent with `odoo_version` if it is installed. If not, walk its
Security and Hygiene checklists yourself before reporting done.

## Anti-patterns

- Writing a field, method, xmlid, or xpath anchor that has no `file:line` in the Brief.
- Reading whole files in core addons "for context" - use the grep table and ranges.
- Guessing an xpath anchor from memory of another version.
- Binding `.sudo()` results to a variable without the `_sudo` suffix, or leaking it out of the method.
- Shipping strings without regenerating the `.pot` and merging the `.po` files.
