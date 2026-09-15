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
method that does not exist in the base addon, an xpath anchor that was never there, an
override hooked on the wrong method, a `sudo()` nobody can audit, a `.pot` that was never
regenerated. The fix is mechanical: **no citation, no code**.

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
3. `grep -n "^version_info" <odoo>/odoo/release.py` in the core checkout the project runs.
4. `'version'` in workspace `__manifest__.py` files, counting only five-part values such as
   `18.0.1.0.0`. Core addons use short values (`sale` is `'1.2'`) that say nothing.
5. Nothing found: ask once, then offer to write `.odoo-version`. Do not silently assume a version.

Then load the `odoo-<major>` skill (`odoo-16` ... `odoo-19`) and read only the guide the task
needs from its `references/`. If the pack is not installed, say so and continue with the trace
below - the real source is the authority; never fill the gap from memory.

Core files moved in Odoo 19 (`odoo/orm/models.py`, `odoo/orm/fields.py`,
`odoo/modules/module_graph.py`; 16-18 use `odoo/models.py`, `odoo/fields.py`,
`odoo/modules/graph.py`). Cite the path that exists in this project, never one recalled from
another version.

## Step 1 - Trace the chain (grep first, read ranges)

Resolve `ROOTS` once, in `addons_path` order: from `*.conf` / `docker-compose*.yml` /
`.claude/odoo.json`; otherwise
`find . -maxdepth 4 -name __manifest__.py -exec dirname {} \; | xargs -n1 dirname | sort -u`.
Core is two roots, `<odoo>/addons` and `<odoo>/odoo/addons` (`base` lives in the second and
Odoo adds it itself, so configs rarely list it). Enterprise and custom addons are roots too.
When two roots contain a module with the same name, the root listed first is the one that runs.

For every model, method, field, or view the task touches, run the commands below. Replace the
uppercase placeholders; escape dots in `MODEL` (`sale\.order`). Keep the quotes around
`--include` globs - unquoted they fail in zsh.

```bash
# 1. Model definition (also matches `_name = _description = '...'`)
grep -rnE --include='*.py' "_name\s*=\s*([A-Za-z_]+\s*=\s*)?['\"]MODEL['\"]" $ROOTS
# 2. Extensions declared on one line
grep -rnE --include='*.py' "_inherit\s*=.*['\"]MODEL['\"]" $ROOTS
# 3. Extensions whose _inherit list spans several lines (hits print as path-NN-)
grep -rnE --include='*.py' -A12 "_inherit\s*=\s*[[(][^])]*$" $ROOTS | grep -E "['\"]MODEL['\"]"
# 4. Delegation: trace every parent model found here like MODEL
grep -nE "_inherits\s*=" MODEL_FILES
# 5. Field definition, plain or annotated (`commercial_partner_id: Partner = fields.Many2one(`)
grep -nE "^\s+FIELD(\s*:\s*[A-Za-z_.]+)?\s*=\s*fields\." MODEL_FILES
# 6. Every definition of a method
grep -nE "^\s+def METHOD\(" MODEL_FILES
# 7. Hooks a method calls: read its range, then list private calls; trace each hook as METHOD
sed -n 'A,Bp' BASE_FILE | grep -nE "\._[a-z_]+\("
# 8. Views on the model
grep -rlE --include='*.xml' "<field name=\"model\">MODEL</field>" $ROOTS
# 9. Every view and QWeb template inheriting VIEW (an unqualified ref counts only inside MODULE)
grep -rnE --include='*.xml' "name=['\"]inherit_id['\"] ref=['\"](MODULE\.)?VIEW['\"]|inherit_id=['\"](MODULE\.)?VIEW['\"]" $ROOTS
# 10. Anchor nodes: run on the base view file and on every file from 9
grep -nE "name=['\"]ANCHOR['\"]|<notebook|<page |<group |<header|<list|<tree" VIEW_FILES
# 11. ACL and record rules (MODEL with dots as underscores)
grep -rn --include='ir.model.access.csv' "model_MODEL_UNDERSCORED," $ROOTS
grep -rln --include='*.xml' "model_MODEL_UNDERSCORED\"" $ROOTS | grep security
# 12. Before renaming or removing FIELD: every use
grep -rnwE --include='*.py' --include='*.xml' --include='*.js' "FIELD" $ROOTS
# 13. Tests to mirror, and JS only if touched
ls BASE_MODULE/tests/; grep -rnE "def test_.*METHOD" MODULE/tests
grep -rnE --include='*.js' "patch\(|registry\.category\(" MODULE/static
```

`MODEL_FILES` are the files from commands 1-3. For command 12, keep hits on MODEL and list
each one: views, QWeb, `@api.depends`, `depends=`, `related=`, domains, record rules, Python,
tests.

**A file often holds several classes.** Before citing a hit, read up to the nearest `class`
line and confirm its `_name` or `_inherit` is MODEL. `addons/stock/models/stock_location.py`
defines `name` once for `stock.location` and again for `stock.route`.

**A class without `_name`.** Odoo 16-18: a one-item `_inherit` gives its name, otherwise the
class name is used verbatim. Odoo 19: only a string `_inherit` gives the name; anything else
derives it from the class name (`ProductTemplateExtra` becomes `product.template.extra`), so
`_inherit = ['product.template']` without `_name` creates a new model in 19. A class with
`_name = MODEL` that also lists MODEL in `_inherit` is an extension.

Reading budget - this is where tokens go:

- Read ranges, not files: `sed -n 'A,Bp'` or Read with offset/limit, at most 120 lines per hop.
- At most 3 hops inline. Deeper or cross-module flows go to the `odoo-code-tracer` agent with
  `odoo_version` set **if it is installed**; otherwise keep going with the commands above.
- Never re-read a file already cited in the Brief.

## Step 2 - Context Brief (no citation, no code)

Write the brief before any code, one row per symbol the change touches (Odoo 18 example):

| Layer | Symbol | Source (file:line) | Base behaviour | Change |
|-------|--------|--------------------|----------------|--------|
| model | `purchase.order` | `addons/purchase/models/purchase_order.py:19` | `_name`, inherits `mail.thread` | inherit |
| method+super | `button_approve` | `purchase_order.py:528`; override `purchase_stock/models/purchase_order.py:117` calls `_create_picking` | pickings exist only with `purchase_stock` | depends `purchase_stock`, call super, then X |
| path | `stock.picking` `partner_id.commercial_partner_id.vat` | `stock/models/stock_picking.py:630` -> `base/models/res_partner.py:304` -> `:247` | Many2one, Many2one, Char | related field |
| view+xpath | `purchase.purchase_order_form` | `purchase/views/purchase_views.xml:130`, anchor `partner_ref` `:185`, one node in the form | - | add field after anchor |

Layers: model / field / method+super / path / view+xpath / security / data / i18n / test.

The **Source** cell holds exactly one of:

- `file:line` - the cited line itself shows the claim (definition, record, anchor node).
- `NOT FOUND` - every relevant command ran over all ROOTS and nothing on MODEL matched. Name the
  closest real symbol when one exists.
- `UNCERTAIN: <what is missing>` - name the file not read, the runtime-built domain, or the
  other module's view that provides the anchor. Never for a question a command above answers.
- `AMBIGUOUS: <modules>` - overrides in modules that do not depend on each other.

Any cell other than `file:line` means no code for that row: drop it, add the missing `depends`,
or ask. More than 15 rows means the task should be split; never drop a row to fit.

Rules:

- **Redefined field.** Cite the first definition and every redefinition. With the same field
  class, attributes not repeated keep their earlier value (`selection_add` extends the list);
  with a different class, earlier attributes are discarded.
- **Path** (`related=`, `@api.depends`, `depends=`, `domain=`, `domain_force`). One citation per
  hop, comodel read from the definition. A non-relational hop ends the path; a missing hop is
  NOT FOUND at that hop.
- **Depends.** A symbol defined only in a module outside the transitive `depends` is not
  guaranteed to be installed, even if it exists in the current database. Add the dependency or
  drop the row.
- **Override order.** Modules load by dependency depth, then name (19 also by phase). The class
  loaded last runs first and its `super()` reaches the earlier ones. Declare `depends` on every
  module whose override the change relies on. Between modules that do not depend on each other
  the order is an accident of depth and name: write AMBIGUOUS, never guess.
- **Generated at install, never in XML.** `<module>.model_<model>`,
  `<module>.field_<model>__<field>`, `<module>.selection__<model>__<field>__<value>` (dots become
  `_`), and `base.module_category_*` from manifest `category`. Cite the model, field, or
  selection they reflect; `<module>` must define or extend that model. Every other xmlid needs
  its `id="..."` record.
- **Magic fields.** `id` and `display_name` exist on every model. `create_uid`, `create_date`,
  `write_uid`, `write_date` exist when `_log_access` is on, the default for regular and transient
  models, off for abstract ones. Cite the explicit definition when the model declares one.
- **Xpath anchor.** The anchor must be in the base view or in an inheriting view of a module in
  `depends`; otherwise UNCERTAIN. A locator matches the first node, so state how many nodes carry
  that name in the combined views.
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
- Override the narrowest hook that runs when the change needs it (command 7), not the public
  method that wraps it. Call `super()` and add the smallest delta; never copy the base body.
- `sudo()` naming: bind any recordset obtained through `sudo()` to a name ending in `_sudo`
  (`partner_sudo = self.partner_id.sudo()`,
  `orders_sudo = self.env['sale.order'].sudo().search(domain)`). A one-shot call
  (`record.sudo().write(vals)`) needs no variable. Never return a `_sudo` recordset from a
  public method or keep it on `self`.
- No `ponytail:` or other "simplified for now" markers in Odoo code - either the code is right
  or the plan in Step 3 says what was deferred.
- New user-facing strings go through `_()` / `_t()` / `string=` / `help=` so they are extractable.

## Step 5 - Definition of done

- [ ] Fresh install whenever the change adds data files, xmlids, views, or security, on a
      throwaway database the project never uses:
      `odoo-bin -c <conf> -d scratch_<module> -i <module> --max-cron-threads=0 --stop-after-init`,
      then `dropdb scratch_<module>`. Installing catches load-order and missing-xmlid errors that
      reading cannot.
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

- Writing a field, method, xmlid, or xpath anchor whose Brief row is not `file:line`.
- Citing a hit without checking which class, and so which model, it belongs to.
- Ordering an override chain from memory or from grep output order instead of `depends`.
- Overriding a public method when the behaviour lives in a hook it calls.
- `UNCERTAIN` without naming what is missing, or for something a Step 1 command answers.
- Reporting `model_*`, `field_*__*`, or magic fields as missing, or inventing any other xmlid.
- Anchoring an xpath on a node that only another module's view adds, without that `depends`.
- Reading whole files in core addons "for context" - use the commands and ranges.
- Binding `.sudo()` results to a variable without the `_sudo` suffix, or leaking it out of the method.
- Shipping strings without regenerating the `.pot` and merging the `.po` files.
