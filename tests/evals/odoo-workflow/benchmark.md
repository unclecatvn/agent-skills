# odoo-workflow benchmark

Run on 2026-09-24 against Odoo community 18.0 (33c7b160) and 19.0 (1a13ceea). Model: Claude Opus 5.5
for every agent. Reproduce the mechanical part with `tests/bench_odoo_workflow.py`.

## 1. Mechanical: 1.0.19 grep recipe vs the 1.0.20 helper

The 1.0.19 Step 1 commands run verbatim (`ROOTS="addons odoo/addons"`, then `$ROOTS`) under zsh, the
shell Claude Code uses on macOS, and under bash, against the helper. 17 questions per version with
answers checked by hand in the source.

| Recipe | Correct | Output bytes | Seconds |
|---|---|---|---|
| zsh | 12/34 | 0 | 0.3 |
| bash | 20/34 | 135155 | 56.6 |
| helper | 34/34 | 12226 | 38.3 |

Under zsh `$ROOTS` is one argument, macOS grep skips the missing path silently, and every lookup
returns nothing: each "exists" question becomes a false NOT FOUND. Under bash the recipe still misses
fields from mixins (`access_url`, `activity_ids`) and prototype parents, xmlids defined in data CSV files,
the base signature of `message_post`, and treats `sale.report.create_date` as a magic field although
`_auto = False` turns log fields off. The helper answers all 34 with about a tenth of the output.

### Odoo 18.0, per question

| Case | Truth | 1.0.19 zsh | 1.0.19 bash | helper | bytes bash / helper | s bash / helper |
|---|---|---|---|---|---|---|
| field `sale.order commitment_date` (own field) | exists | **false NOT FOUND** | ok | ok | 4119 / 130 | 2.7 / 1.3 |
| field `sale.order delivery_date` (invented field) | absent | ok | ok | ok | 4043 / 149 | 1.7 / 1.4 |
| field `res.partner country_id` (annotated definition) | exists | **false NOT FOUND** | ok | ok | 15227 / 150 | 1.7 / 1.7 |
| field `sale.order access_url` (from portal.mixin) | exists | **false NOT FOUND** | **false NOT FOUND** | ok | 4043 / 188 | 1.7 / 1.5 |
| field `sale.order activity_ids` (from mail.activity.mixin) | exists | **false NOT FOUND** | **false NOT FOUND** | ok | 4043 / 227 | 1.7 / 1.4 |
| field `sale.order campaign_id` (redefined, comodel in utm.mixin) | exists | **false NOT FOUND** | ok | ok | 4135 / 332 | 1.7 / 1.4 |
| field `event.booth booth_category_id` (from prototype parent) | exists | **false NOT FOUND** | **false NOT FOUND** | ok | 236 / 221 | 1.7 / 1.2 |
| field `event.type.booth partner_id` (only on the prototype copy) | absent | ok | **invented** | ok | 374 / 301 | 1.6 / 0.3 |
| field `sale.order.line create_date` (magic, _log_access) | exists | ok | ok | ok | 3153 / 276 | 1.7 / 0.5 |
| field `sale.report create_date` (magic off, _auto = False) | absent | **invented** | **invented** | ok | 496 / 314 | 1.6 / 0.4 |
| field `res.partner country` (invented hop) | absent | ok | ok | ok | 14915 / 110 | 1.7 / 1.5 |
| xmlid `base lang_vi_VN` (record in a data CSV) | exists | **false NOT FOUND** | **false NOT FOUND** | ok | 0 / 192 | 0.9 / 0.3 |
| xmlid `sales_team group_sale_manager` (record in XML) | exists | **false NOT FOUND** | ok | ok | 114 / 378 | 0.4 / 0.2 |
| xmlid `sales_team group_sale_admin` (invented group) | absent | ok | ok | ok | 0 / 194 | 0.4 / 0.2 |
| method `sale.order message_post` (base def in mail.thread) | exists | **false NOT FOUND** | **false NOT FOUND** | ok | 4119 / 1341 | 1.7 / 1.4 |
| method `sale.order _action_confirm` (own hook) | exists | **false NOT FOUND** | ok | ok | 4561 / 1358 | 1.8 / 1.4 |
| method `sale.order action_invented` (invented method) | absent | ok | ok | ok | 4043 / 126 | 1.7 / 1.4 |

### Odoo 19.0, per question

| Case | Truth | 1.0.19 zsh | 1.0.19 bash | helper | bytes bash / helper | s bash / helper |
|---|---|---|---|---|---|---|
| field `sale.order commitment_date` (own field) | exists | **false NOT FOUND** | ok | ok | 3956 / 129 | 3.3 / 1.5 |
| field `sale.order delivery_date` (invented field) | absent | ok | ok | ok | 3881 / 149 | 1.9 / 1.6 |
| field `res.partner country_id` (annotated definition) | exists | **false NOT FOUND** | ok | ok | 15666 / 362 | 1.9 / 2.2 |
| field `sale.order access_url` (from portal.mixin) | exists | **false NOT FOUND** | **false NOT FOUND** | ok | 3881 / 188 | 1.9 / 1.6 |
| field `sale.order activity_ids` (from mail.activity.mixin) | exists | **false NOT FOUND** | **false NOT FOUND** | ok | 3881 / 227 | 2.0 / 1.6 |
| field `sale.order campaign_id` (redefined, comodel in utm.mixin) | exists | **false NOT FOUND** | ok | ok | 3973 / 332 | 1.9 / 1.6 |
| field `event.booth booth_category_id` (from prototype parent) | exists | **false NOT FOUND** | **false NOT FOUND** | ok | 236 / 225 | 1.9 / 1.4 |
| field `event.type.booth partner_id` (only on the prototype copy) | absent | ok | **invented** | ok | 374 / 301 | 1.9 / 0.4 |
| field `sale.order.line create_date` (magic, _log_access) | exists | ok | ok | ok | 3632 / 284 | 1.9 / 0.7 |
| field `sale.report create_date` (magic off, _auto = False) | absent | **invented** | **invented** | ok | 496 / 318 | 1.9 / 0.4 |
| field `res.partner country` (invented hop) | absent | ok | ok | ok | 15208 / 110 | 2.0 / 2.3 |
| xmlid `base lang_vi_VN` (record in a data CSV) | exists | **false NOT FOUND** | **false NOT FOUND** | ok | 0 / 192 | 1.0 / 0.3 |
| xmlid `sales_team group_sale_manager` (record in XML) | exists | **false NOT FOUND** | ok | ok | 114 / 378 | 0.6 / 0.2 |
| xmlid `sales_team group_sale_admin` (invented group) | absent | ok | ok | ok | 0 / 194 | 0.5 / 0.2 |
| method `sale.order message_post` (base def in mail.thread) | exists | **false NOT FOUND** | **false NOT FOUND** | ok | 3957 / 1368 | 2.0 / 1.8 |
| method `sale.order _action_confirm` (own hook) | exists | **false NOT FOUND** | ok | ok | 4398 / 1356 | 1.9 / 1.6 |
| method `sale.order action_invented` (invented method) | absent | ok | ok | ok | 3881 / 126 | 1.9 / 1.6 |

### Real projects: do the resolved roots include the Odoo core?

| Workspace | 1.0.19 fallback roots | core? | helper roots | core? |
|---|---|---|---|---|
| dtg | ./erp, ./erp-external, ./erp-internal | **no** | 5 roots | yes |
| ucat_labs | ./erp, ./erp-external, ./erp-internal | **no** | 6 roots | yes |
| app-odoo-ucat | . | **no** | 6 roots | yes |

In all three projects the conf lives in the core checkout (`../18.0/odoo.conf`, `../19.0/odoo.conf`),
so the 1.0.19 fallback (`find . -name __manifest__.py`) returns custom roots only and every core
symbol would be NOT FOUND. The helper resolves them from `.claude/launch.json` or conf discovery.

## 2. Agents, 1.0.19 vs 1.0.20, environment given

24 evals from `evals.json`, each run once with the 1.0.19 skill and packs and once with the 1.0.20
skill and packs, same workspace, and the prompt names the Odoo source path and conf. A separate grader
saw both answers blind (A/B swapped by eval id), checked claims against the source, and scored the
expectations.

| Eval | Odoo | 1.0.19 pass | new pass | 1.0.19 invented / wrong cite | new invented / wrong cite | better | 1.0.19 tools / out tok | new tools / out tok |
|---|---|---|---|---|---|---|---|---|
| 1 field-that-does-not-exist | 18.0 | 3/3 | 3/3 | 0 / 0 | 0 / 0 | old | 27 / 22998 | 20 / 16421 |
| 2 anchor-added-by-another-module | 18.0 | 3/3 | 3/3 | 0 / 0 | 0 / 0 | new | 31 / 23160 | 22 / 26585 |
| 3 existing-view-inheritors | 18.0 | 3/3 | 3/3 | 0 / 0 | 0 / 0 | new | 24 / 18735 | 30 / 26582 |
| 4 hook-not-public-method | 18.0 | 3/3 | 3/3 | 1 / 0 | 0 / 0 | new | 29 / 23875 | 30 / 30757 |
| 5 partial-field-override | 18.0 | 3/3 | 3/3 | 0 / 0 | 0 / 0 | new | 9 / 6655 | 8 / 4790 |
| 6 broken-path-hop | 18.0 | 3/3 | 3/3 | 0 / 0 | 0 / 0 | new | 25 / 14670 | 29 / 21051 |
| 7 group-xmlid-that-does-not-exist | 18.0 | 2/2 | 2/2 | 0 / 0 | 1 / 0 | old | 31 / 15158 | 22 / 16819 |
| 8 generated-model-xmlid | 18.0 | 3/3 | 3/3 | 0 / 0 | 0 / 0 | new | 16 / 10890 | 20 / 14905 |
| 9 magic-field | 18.0 | 3/3 | 3/3 | 0 / 1 | 0 / 0 | new | 45 / 29453 | 37 / 32360 |
| 10 annotated-field-definition | 18.0 | 3/3 | 3/3 | 0 / 0 | 0 / 0 | old | 7 / 3663 | 8 / 3434 |
| 11 impact-before-rename | 18.0 | 4/4 | 4/4 | 0 / 0 | 1 / 0 | old | 32 / 28463 | 22 / 30244 |
| 12 nameless-class-by-version | 19.0 | 2/2 | 2/2 | 0 / 0 | 0 / 0 | old | 12 / 7122 | 8 / 4320 |
| 13 field-from-mixin | 18.0 | 3/3 | 3/3 | 0 / 1 | 0 / 0 | new | 27 / 16630 | 19 / 15866 |
| 14 prototype-copy-is-another-model | 18.0 | 3/3 | 3/3 | 1 / 0 | 0 / 0 | new | 18 / 14474 | 21 / 21268 |
| 15 xmlid-defined-in-csv | 18.0 | 3/3 | 3/3 | 0 / 0 | 0 / 0 | old | 7 / 3782 | 6 / 3421 |
| 16 report-model-has-no-create-date | 18.0 | 3/3 | 3/3 | 0 / 0 | 0 / 0 | new | 45 / 26812 | 23 / 22999 |
| 17 owl-template-inheritors | 18.0 | 3/3 | 3/3 | 0 / 0 | 0 / 0 | old | 15 / 9976 | 16 / 10459 |
| 18 controller-route-override | 18.0 | 3/3 | 3/3 | 0 / 0 | 0 / 0 | new | 21 / 19969 | 29 / 28762 |
| 19 odoo19-po-export | 19.0 | 3/3 | 3/3 | 0 / 0 | 0 / 0 | old | 20 / 18256 | 15 / 13326 |
| 20 multi-company-new-model | 18.0 | 3/3 | 3/3 | 0 / 0 | 1 / 0 | new | 23 / 21123 | 25 / 24118 |
| 21 portal-sudo-needs-access-check | 18.0 | 3/3 | 3/3 | 0 / 0 | 0 / 0 | tie | 37 / 25620 | 32 / 30158 |
| 22 traceback-entry | 18.0 | 2/3 | 3/3 | 2 / 0 | 0 / 0 | new | 15 / 16611 | 20 / 21814 |
| 23 odoo19-sql-constraint | 19.0 | 2/2 | 2/2 | 0 / 0 | 0 / 0 | old | 30 / 17707 | 24 / 13724 |
| 24 mixin-method-signature | 18.0 | 4/4 | 4/4 | 1 / 0 | 1 / 0 | new | 34 / 26335 | 25 / 21059 |

| | 1.0.19 | new |
|---|---|---|
| Expectations passed | 70/71 (99%) | 71/71 (100%) |
| Evals fully passed | 23/24 | 24/24 |
| Invented Odoo symbols | 5 | 4 |
| Wrong file:line citations | 2 | 0 |
| Grader prefers | 9 | 14 (ties 1) |
| Tool calls (total) | 580 | 511 |
| Output tokens (total) | 422137 | 455242 |
| Context tokens processed (total) | 46338875 | 43080187 |

Output tokens are per run; context tokens sum what every turn processed, cache reads included.

## 3. Agents, 1.0.19 vs 1.0.20, realistic setup

Eight evals that depend on reaching the core, run the same way, but the prompt names only the
workspace. The conf sits in a sibling directory (`../conf/odoo18.conf`), as in the user's projects,
and nothing says where the Odoo source is.

| Eval | Odoo | 1.0.19 pass | new pass | 1.0.19 invented / wrong cite | new invented / wrong cite | better | 1.0.19 tools / out tok | new tools / out tok |
|---|---|---|---|---|---|---|---|---|
| 1 field-that-does-not-exist | 18.0 | 3/3 | 3/3 | 0 / 0 | 0 / 0 | new | 28 / 20421 | 26 / 19959 |
| 6 broken-path-hop | 18.0 | 3/3 | 3/3 | 0 / 0 | 0 / 0 | tie | 28 / 17828 | 21 / 25111 |
| 7 group-xmlid-that-does-not-exist | 18.0 | 2/2 | 2/2 | 0 / 0 | 0 / 0 | old | 26 / 15212 | 31 / 17764 |
| 9 magic-field | 18.0 | 3/3 | 3/3 | 0 / 0 | 0 / 0 | old | 38 / 30552 | 26 / 32564 |
| 13 field-from-mixin | 18.0 | 3/3 | 3/3 | 0 / 0 | 0 / 0 | tie | 29 / 16641 | 21 / 15994 |
| 14 prototype-copy-is-another-model | 18.0 | 3/3 | 3/3 | 0 / 0 | 0 / 0 | new | 23 / 18102 | 19 / 19103 |
| 15 xmlid-defined-in-csv | 18.0 | 3/3 | 3/3 | 0 / 0 | 0 / 0 | tie | 13 / 5393 | 6 / 3401 |
| 16 report-model-has-no-create-date | 18.0 | 3/3 | 3/3 | 0 / 0 | 0 / 0 | new | 35 / 22594 | 30 / 27238 |

| | 1.0.19 | new |
|---|---|---|
| Expectations passed | 23/23 (100%) | 23/23 (100%) |
| Evals fully passed | 8/8 | 8/8 |
| Invented Odoo symbols | 0 | 0 |
| Wrong file:line citations | 0 | 0 |
| Grader prefers | 2 | 3 (ties 3) |
| Tool calls (total) | 220 | 180 |
| Output tokens (total) | 146743 | 161134 |
| Context tokens processed (total) | 17635571 | 14833225 |

Both versions located the core in 8 of 8 runs (graded `found_core`): the 1.0.19 agents found it by
exploring, the 1.0.20 agents through `odoo_trace env`.

## 4. Without any skill vs with odoo-workflow 1.0.20

The same evals run by a plain agent that gets only the user's request: no workflow skill and no Odoo
pack. The with-skill answers are the 1.0.20 runs of sections 2 and 3. A grader saw each pair as A/B
(order swapped by eval id), checked every claim against the source, and also judged whether the code
or commands would ship broken.

### Realistic setup (8 evals, the agent is not told where Odoo is)

| Eval | Without skill | With skill | Invented (without / with) | Grader prefers | Tool calls (without / with) | Output tokens (without / with) |
|---|---|---|---|---|---|---|
| 1 field-that-does-not-exist | 3/3 | 3/3 | 0 / 0 | with | 14 / 26 | 8k / 20k |
| 6 broken-path-hop | 2/3 | 3/3 | 0 / 0 | with | 6 / 21 | 6k / 25k |
| 7 group-xmlid-that-does-not-exist | 2/2 | 2/2 | 0 / 0 | with | 27 / 31 | 11k / 18k |
| 9 magic-field | 2/3 | 3/3 | 0 / 0 | with | 3 / 26 | 14k / 33k |
| 13 field-from-mixin | 3/3 | 3/3 | 0 / 0 | with | 13 / 21 | 11k / 16k |
| 14 prototype-copy-is-another-model | 3/3 | 3/3 | 0 / 0 | with | 11 / 19 | 8k / 19k |
| 15 xmlid-defined-in-csv | 3/3 | 3/3 | 0 / 0 | without | 8 / 6 | 4k / 3k |
| 16 report-model-has-no-create-date | 3/3 | 3/3 | 0 / 0 | with | 26 / 30 | 17k / 27k |

### Environment given (24 evals, the prompt names the Odoo source and conf)

| Eval | Without skill | With skill | Invented (without / with) | Grader prefers | Tool calls (without / with) | Output tokens (without / with) |
|---|---|---|---|---|---|---|
| 1 field-that-does-not-exist | 3/3 | 3/3 | 0 / 0 | tie | 9 / 20 | 7k / 16k |
| 2 anchor-added-by-another-module | 3/3 | 3/3 | 0 / 0 | with | 9 / 22 | 9k / 27k |
| 3 existing-view-inheritors | 3/3 | 3/3 | 0 / 0 | with | 16 / 30 | 11k / 27k |
| 4 hook-not-public-method | 3/3 | 3/3 | 0 / 0 | tie | 24 / 30 | 20k / 31k |
| 5 partial-field-override | 3/3 | 3/3 | 0 / 0 | tie | 6 / 8 | 4k / 5k |
| 6 broken-path-hop | 3/3 | 3/3 | 0 / 0 | with | 6 / 29 | 5k / 21k |
| 7 group-xmlid-that-does-not-exist | 2/2 | 2/2 | 0 / 0 | tie | 13 / 22 | 6k / 17k |
| 8 generated-model-xmlid | 3/3 | 3/3 | 1 / 0 | with | 5 / 20 | 3k / 15k |
| 9 magic-field | 2/3 | 3/3 | 0 / 0 | with | 28 / 37 | 18k / 32k |
| 10 annotated-field-definition | 3/3 | 3/3 | 1 / 0 | with | 4 / 8 | 2k / 3k |
| 11 impact-before-rename | 4/4 | 4/4 | 0 / 1 | without | 8 / 22 | 12k / 30k |
| 12 nameless-class-by-version | 2/2 | 2/2 | 0 / 0 | without | 16 / 8 | 6k / 4k |
| 13 field-from-mixin | 3/3 | 3/3 | 0 / 0 | tie | 10 / 19 | 6k / 16k |
| 14 prototype-copy-is-another-model | 3/3 | 3/3 | 0 / 0 | tie | 11 / 21 | 5k / 21k |
| 15 xmlid-defined-in-csv | 3/3 | 3/3 | 0 / 0 | tie | 4 / 6 | 3k / 3k |
| 16 report-model-has-no-create-date | 3/3 | 3/3 | 0 / 0 | with | 25 / 23 | 14k / 23k |
| 17 owl-template-inheritors | 3/3 | 3/3 | 0 / 0 | without | 10 / 16 | 7k / 10k |
| 18 controller-route-override | 3/3 | 3/3 | 0 / 0 | without | 12 / 29 | 9k / 29k |
| 19 odoo19-po-export | 3/3 | 3/3 | 1 / 0 | with | 15 / 15 | 12k / 13k |
| 20 multi-company-new-model | 3/3 | 3/3 | 0 / 1 | tie | 14 / 25 | 10k / 24k |
| 21 portal-sudo-needs-access-check | 3/3 | 3/3 | 0 / 0 | tie | 18 / 32 | 15k / 30k |
| 22 traceback-entry | 3/3 | 3/3 | 1 / 0 | with | 10 / 20 | 7k / 22k |
| 23 odoo19-sql-constraint | 2/2 | 2/2 | 0 / 0 | tie | 14 / 24 | 7k / 14k |
| 24 mixin-method-signature | 4/4 | 4/4 | 0 / 0 | without | 18 / 25 | 16k / 21k |

| | Without skill | With odoo-workflow |
|---|---|---|
| Expectations passed, realistic setup | 21/23 | 23/23 |
| Evals fully passed, realistic setup | 6/8 | 8/8 |
| Expectations passed, environment given | 70/71 | 71/71 |
| Evals fully passed, environment given | 23/24 | 24/24 |
| Invented Odoo behaviour (all 32 runs) | 4 | 2 |
| Code or commands that would ship broken | 0 | 0 |
| Grader prefers (32 pairs) | 6 | 16 (10 ties) |
| Tool calls (32 runs) | 413 | 691 |
| Output tokens (32 runs) | 293k | 616k |

Without the skill, Opus is already careful when it can read the source: no answer shipped broken code.
The skill's gain is grounding and completeness: every answer cites the source, it asks for or adds the
migration a stored field on a populated table needs, and it tests on a throwaway database with a
check that tests really ran. It costs about twice the output tokens and 1.7 times the tool calls.

## Reading the numbers

- Answer quality with Opus: both versions pass nearly every expectation (70/71 vs 71/71 with the
  environment given, 23/23 each in the realistic run). A strong model compensates for the old
  recipe: it notices empty greps, types paths itself, explores for the core and reads the source. On
  these evals quality sits at the ceiling, so they cannot show a larger gap.
- Where 1.0.20 is measurably better: the recipe itself (34/34 vs 12/34 under zsh), wrong citations
  (0 vs 2), the one eval where the old run reasoned from memory (22: two false claims about the
  merged form), and cost: 12% fewer tool calls and 7% less context with the environment given, 18%
  fewer tool calls and 16% less context in the realistic run, for about 8-10% more output tokens
  (longer Briefs and definition-of-done sections).
- Not covered by these evals: the definition-of-done commands, which were instead run end to end on
  scratch databases (install and tests, upgrade with and without a migration, i18n, drop, hygiene)
  and corrected where Odoo behaved differently from the text.
- One run per eval and variant, one model: differences of one expectation are noise. Weaker models,
  or harder multi-step evals, are the next thing to measure.
