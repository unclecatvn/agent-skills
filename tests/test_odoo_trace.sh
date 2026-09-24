#!/usr/bin/env bash
# Checks skills/odoo-workflow/scripts/odoo_trace.py on tests/fixtures/odoo_trace (a fake core
# checkout in core/ plus custom addons in custom/), and on real checkouts when ODOO_ROOT_18 /
# ODOO_ROOT_19 point at Odoo source trees. Runs under bash and zsh:
#   bash tests/test_odoo_trace.sh
#   ODOO_ROOT_18=/path/to/odoo/18.0 ODOO_ROOT_19=/path/to/odoo/19.0 zsh tests/test_odoo_trace.sh
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
TRACE="$HERE/../skills/odoo-workflow/scripts/odoo_trace.py"
PY=${PYTHON:-python3}
export PYTHONDONTWRITEBYTECODE=1  # keep __pycache__ out of the shipped skill folder
# a temp copy, so no .claude/ config in a parent directory changes what the helper resolves
WORK=$(mktemp -d "${TMPDIR:-/tmp}/odoo_trace.XXXXXX")
trap 'rm -rf "$WORK"' EXIT
cp -R "$HERE/fixtures/odoo_trace/." "$WORK/"
passes=0
fails=0

run() { # DIR ARGS...: runs the helper in DIR, sets OUT (stdout+stderr) and RC
  local dir=$1
  shift
  OUT=$(cd "$dir" && "$PY" "$TRACE" "$@" 2>&1)
  RC=$?
}
expect() { # NAME, EXIT CODE, extended regexes that some output line must match
  local name=$1 code=$2 rx
  shift 2
  for rx in "$@"; do
    if [ "$RC" != "$code" ] || ! printf '%s\n' "$OUT" | grep -qE -- "$rx"; then
      echo "FAIL $name (exit $RC, want $code; missing /$rx/)"
      printf '%s\n' "$OUT" | head -20 | sed 's/^/    /'
      fails=$((fails + 1))
      return
    fi
  done
  passes=$((passes + 1))
}
refute() { # NAME, extended regex no output line may match
  if printf '%s\n' "$OUT" | grep -qE -- "$2"; then
    echo "FAIL $1 (unexpected /$2/)"
    fails=$((fails + 1))
  else
    passes=$((passes + 1))
  fi
}

C="$WORK/custom"

# runtime resolution: the only conf whose addons_path covers cwd (core/odoo.conf, relative entries)
run "$C" env
expect "env discovers core/odoo.conf" 0 '^conf +.*/core/odoo\.conf +\[discovered' '^dev_db +fixture_db' \
  '^  r1 .*/core/odoo/addons ' '^  r2 .*/core/addons ' '^  r3 .*/custom ' '^VERDICT: Odoo 18\.0, 3 roots' \
  '^note: relative addons_path entries of .*/core/odoo\.conf resolved against its directory'
run "$C/sale_custom/models" env
expect "env walks up to the nearest ancestor holding a covering conf" 0 '^conf +.*/core/odoo\.conf +\[discovered'
ROOTS=$(cd "$C" && "$PY" "$TRACE" roots 2>/dev/null)
OUT=$ROOTS RC=0
expect "roots prints only paths, core first" 0 '/core/odoo/addons$' '/custom$'
refute "roots keeps VERDICT off stdout" 'VERDICT'
OUT=$(grep -rl --include='*.py' "_name = 'sale.order'" $(cd "$C" && "$PY" "$TRACE" roots 2>/dev/null)) RC=0
expect "\$(roots) splits into grep paths" 0 'sale/models/sale_order\.py$'

# models: multi-line _inherit, unimported file, prototype copies, comodel_name is no definition
run "$C" model sale.order
expect "model sale.order" 0 'sale/models/sale_order\.py:10 sale SaleOrder define _inherit=\[portal\.mixin, mail\.thread\]$' \
  'sale/models/unused\.py:4 sale SaleOrder extend UNIMPORTED' \
  'sale_custom/models/broken\.py: ' \
  'SaleOrderMixed copies sale\.order into SaleOrderMixed: not sale\.order' \
  '^VERDICT: sale\.order defined in sale \(.*sale_order\.py:10\); 3 extensions$'
run "$C" model event.type.booth
expect "model: prototype copy is not an extension" 0 \
  'event_booth\.py:4 event_booth EventBooth copies event\.type\.booth into event\.booth' '; 0 extensions$'
run "$C" model sale.team
expect "model: comodel_name= is not a definition" 1 '^VERDICT: NOT FOUND: model sale\.team has no definition'
run "$C" model sale.custom.tag
expect "model: chained _name = _description" 0 'sale_custom SaleCustomTag define$'

# fields: parents, prototype copies, annotated, _inherits, magic, _auto=False, selection keys
run "$C" field sale.order access_url
expect "field via mixin" 0 'portal_mixin\.py:8 portal PortalMixin via=parent portal\.mixin Char compute=' \
  '^VERDICT: FOUND via parent portal\.mixin$'
run "$C" field sale.order delivery_date
expect "field NOT FOUND suggests by label" 1 "^VERDICT: NOT FOUND: sale\.order\.delivery_date; closest fields: commitment_date \(label 'Delivery Date'\)"
refute "suggestions skip unimported classes" 'never_loaded'
run "$C" field event.type.booth partner_id
expect "field on a copy is not on the parent" 1 '^note: partner_id is defined on event\.booth' '^VERDICT: NOT FOUND'
run "$C" field event.booth booth_category_id
expect "field from the copied parent" 0 '^VERDICT: FOUND via parent event\.type\.booth$'
run "$C" field res.partner country_id
expect "annotated field" 0 "res_partner\.py:9 base Partner via=self Many2one\('res\.country'\)"
run "$C" field res.users country_id
expect "field through _inherits" 0 '^VERDICT: FOUND via _inherits res\.partner \(partner_id\)$'
run "$C" field sale.order partner_id
expect "redefinition without comodel" 0 'sale_stock SaleOrder via=self Many2one comodel from .*sale/models/sale_order\.py:20$'
run "$C" field sale.order.line create_date
expect "magic log field" 0 'odoo/models\.py:12 core MetaModel via=magic Datetime' '^VERDICT: FOUND magic$'
run "$C" field sale.report create_date
expect "_auto=False has no log fields" 1 'sale_report\.py:7 has _auto=False' 'odoo/models\.py:10\)$'
run "$C" field sale.order state
expect "selection keys from a module constant" 0 "selection=\['draft', 'sale', 'cancel'\]" "selection_add=\['shipped'\]"
run "$C" field res.partner name
expect "field redefined with another class" 0 \
  '^final class Text from .*sale_custom/models/res_partner\.py:8; the older defs of another class lose their attributes \(.*odoo/fields\.py:8\)$'
run "$C" field sale.order.line order_partner_id
expect "related field takes its comodel from the path" 0 'Many2one related=.order_id\.partner_id. comodel res\.partner via related$'

# field paths: one hop per model, stop at a missing or non-relational hop
run "$C" field sale.order partner_id.country_id
expect "path of two hops" 0 '^hop 2 res\.partner\.country_id$' \
  '^VERDICT: FOUND sale\.order\.partner_id\.country_id: Many2one\(res\.partner\) > Many2one\(res\.country\)$'
run "$C" field sale.order.line order_partner_id.country_id
expect "path through a related many2one" 0 '^VERDICT: FOUND .*: Many2one\(res\.partner\) > Many2one\(res\.country\)$'
run "$C" field sale.order create_uid.name
expect "path through a magic field and _inherits" 0 '^VERDICT: FOUND sale\.order\.create_uid\.name: Many2one\(res\.users\) > Text$'
run "$C" field sale.order partner_id.nope
expect "path with a missing hop" 1 '^VERDICT: NOT FOUND: res\.partner\.nope \(hop 2 of sale\.order\.partner_id\.nope\)'
run "$C" field sale.order state.name
expect "path through a non-relational hop" 1 '^VERDICT: NOT FOUND: sale\.order\.state is Selection, not relational'

# methods: super() order, hooks at absolute lines, base extensions, core BaseModel, --module
run "$C" method sale.order _action_confirm --module sale_custom
expect "method order and ambiguity" 0 '^#1 .*sale_custom SaleOrder def _action_confirm\(self\) super=yes \[in depends of sale_custom\] hooks: _notify_custom:11$' \
  '^#4 .*sale/models/sale_order\.py:29 sale SaleOrder def _action_confirm\(self\) super=no' \
  '^AMBIGUOUS sale_other / sale_stock: '
run "$C" method sale.order action_confirm
expect "private hooks at absolute lines" 0 'hooks: _check_state:24 _action_confirm:26$'
run "$C" method sale.order write
expect "core BaseModel runs last" 0 '^#1 .*mail MailThread def write' '^#2 .*odoo/models\.py:22 core BaseModel def write\(self, vals\) super=no hooks: _validate_fields:23$'
run "$C" method sale.order _valid_field_parameter
expect "'base' extensions before the core" 0 '^#1 .*mail/models/models\.py:7 mail Base ' '^#2 .*core BaseModel '
run "$C" method sale.order message_post
expect "mixin signature" 0 "mail MailThread @api\.returns def message_post\(self, \*, body='', subject=None"
run "$C" method sale.order nope
expect "missing method" 1 '^VERDICT: NOT FOUND: sale\.order\.nope'

# load order and xmlids
run "$C" depends sale_custom
expect "depends load order" 0 '^  5 sale_other d4 r3$' '^  6 sale_stock d4 r2$' '^  7 sale_custom d5 r3$'
run "$C" xmlid base.lang_vi_VN
expect "xmlid in a CSV" 0 'base/data/res\.lang\.csv:3 base base\.lang_vi_VN$'
run "$C" xmlid sale.group_sale_admin
expect "xmlid NOT FOUND with suggestions" 1 'closest in sale: .*group_sale_manager'
run "$C" xmlid sale.group_sale_manager
expect "xmlid overridden elsewhere" 0 'sale_custom_data\.xml:3 sale_custom overrides sale\.group_sale_manager$'
run "$C" xmlid sale.orphan_record
expect "xmlid only in an unlisted file" 1 'orphan\.xml:3 sale orphan_record \(file not in manifest' \
  '^VERDICT: NOT FOUND: sale\.orphan_record is only in files missing from the manifest'
run "$C" xmlid sale_stock.model_sale_order
expect "generated model xmlid" 0 '^VERDICT: GENERATED sale_stock\.model_sale_order at install: sale_stock extends sale\.order'
run "$C" xmlid sale.field_sale_order__access_url
expect "generated field xmlid on the defining module" 0 '^VERDICT: GENERATED .*model\._original_module'
run "$C" xmlid portal.field_sale_order__access_url
expect "no field xmlid for a module loaded before the model" 1 '^VERDICT: NOT FOUND'
run "$C" xmlid sale.selection__sale_order__state__draft
expect "generated selection xmlid" 0 '^VERDICT: GENERATED .*static selection'
run "$C" xmlid sale_stock.selection__sale_order__state__shipped
expect "generated selection_add xmlid" 0 '^VERDICT: GENERATED .*sale_stock declares value'
run "$C" xmlid sale_stock.field_sale_order__partner_id
expect "generated field xmlid on a redefining module" 0 '^VERDICT: GENERATED .*module in field\._modules'
run "$C" xmlid base.module_category_sales_sales
expect "generated category xmlid" 0 "^VERDICT: GENERATED .*category 'Sales/Sales'"

# files that never load
run "$C" unlisted sale
expect "unlisted files" 0 'sale/data/orphan\.xml not in manifest' 'sale/models/unused\.py never imported' \
  'static/src/legacy/orphan\.js in no assets bundle' '^VERDICT: sale: 3 files never load$'
mkdir -p "$C/sale_other/extra"
for i in 1 2 3 4 5 6; do printf '<odoo/>\n' > "$C/sale_other/extra/f$i.xml"; done
run "$C" unlisted sale_other
expect "unlisted groups a big directory" 0 '/sale_other/extra/ 6 files not in manifest data/demo \(--all lists them\), e\.g\. f1\.xml$'
run "$C" unlisted sale_other --all
expect "unlisted --all lists each file" 0 '/sale_other/extra/f6\.xml not in manifest data/demo$' '^VERDICT: sale_other: 6 files'
rm -r "$C/sale_other/extra"

# Odoo 19 naming and roots
run "$C" --version 19.0 model res.partner
expect "19: a one-item _inherit list without _name is a new model" 0 \
  'ResPartnerExtra copies res\.partner into res\.partner\.extra: not res\.partner'
run "$C" --version 19.0 model sale.order
expect "19: class-derived name" 0 'SaleOrderMixed copies sale\.order into sale\.order\.mixed'
run "$C" --version 19.0 --odoo-root "$WORK/core" --addons "$C" env
expect "19 appends <root>/addons" 0 '^  r2 .*/custom ' '^  r3 .*/core/addons .*auto-added by Odoo 19'
run "$C" --odoo-root "$WORK/core" --addons "$C" env
expect "18 adds only odoo/addons" 0 '^VERDICT: Odoo 18\.0, 2 roots'
run "$C" --odoo-root "$WORK/core" --addons "$WORK/cust*" env
expect "18 takes an addons_path glob literally" 0 '^  skipped .*/cust\* ' '^VERDICT: Odoo 18\.0, 1 roots' \
  '^python +- +\[not found\]$'
run "$C" --version 19.0 --odoo-root "$WORK/core" --addons "$WORK/cust*" env
expect "19 expands an addons_path glob" 0 '^  r2 .*/custom  \[addons_path\]' '^note: --version 19\.0 overrides 18\.0'

# hub models: 15 extensions, the rest summed up by module unless --all
i=1
while [ $i -le 16 ]; do
  mkdir -p "$WORK/many/x_ext_$i"
  printf "{'name': 'x', 'depends': ['sale']}\n" > "$WORK/many/x_ext_$i/__manifest__.py"
  printf "from odoo import models\n\n\nclass SaleOrder(models.Model):\n    _inherit = 'sale.order'\n" \
    > "$WORK/many/x_ext_$i/__init__.py"
  i=$((i + 1))
done
run "$C" --odoo-root "$WORK/core" --addons "$WORK/core/addons,$C,$WORK/many" model sale.order
expect "model caps extensions, core ones hidden first" 0 '^\+4 more extensions \(--all lists them\) in: sale_stock, ' \
  'UNIMPORTED' '^VERDICT: .*; 19 extensions$'
run "$C" --odoo-root "$WORK/core" --addons "$WORK/core/addons,$C,$WORK/many" model sale.order --all
expect "model --all" 0 'sale_stock SaleOrder extend'
refute "model --all prints no summary" '^\+[0-9]+ more'
rm -r "$WORK/many"

# a module in two roots: the first root wins
mkdir -p "$WORK/later"
cp -R "$C/sale_other" "$WORK/later/"
run "$C" --odoo-root "$WORK/core" --addons "$WORK/core/addons,$C,$WORK/later" model sale.order
expect "shadowed module copy" 0 '^shadowed: sale_other also at .*/later/sale_other ' '^VERDICT: .*; 3 extensions$'
rm -r "$WORK/later"

# explicit config files
mkdir -p "$C/.claude"
printf '{"odoo_version": "18.0", "odoo_root": "../core", "dev_db": "json_db", "addons": ["../custom"]}\n' > "$C/.claude/odoo.json"
printf '# pinned by an earlier release\n18.0\n' > "$C/.odoo-version"
run "$C" env
expect ".claude/odoo.json wins" 0 '^version +18\.0 +\[.*odoo\.json\]' '^dev_db +json_db' '^VERDICT: Odoo 18\.0, 2 roots'
printf '{"odoo_version": "19.0", "odoo_root": "../core"}\n' > "$C/.claude/odoo.json"
run "$C" env
expect ".claude/odoo.json disagreeing with release.py" 2 \
  '^SETUP ERROR: version sources disagree: 19\.0 in .*odoo\.json, but 18\.0 in .*/core/odoo/release\.py'
rm "$C/.claude/odoo.json"
run "$C" env
expect ".odoo-version read after .claude/odoo.json" 0 '^version +18\.0 +\[.*/custom/\.odoo-version\]'
printf '17.0\n' > "$C/.odoo-version"
run "$C/sale_custom" env
expect ".odoo-version disagreeing with release.py" 2 '^SETUP ERROR: version sources disagree: 17\.0 in .*\.odoo-version, but 18\.0 in '
printf 'eighteen\n' > "$C/.odoo-version"
run "$C" env
expect ".odoo-version that is no version" 2 "odoo-version: 'eighteen' is not an Odoo version"
rm "$C/.odoo-version"
printf '{"configurations": [{"name": "dev", "runtimeExecutable": "python3", "runtimeArgs": ["../core/odoo-bin", "-c", "../core/odoo.conf", "-d", "launch_db"]}]}\n' > "$C/.claude/launch.json"
run "$C" env
expect ".claude/launch.json odoo-bin config" 0 '^odoo_root .*/core +\[.*launch\.json config "dev"\]' '^dev_db +launch_db' '^python +python3'
rm -r "$C/.claude"

# setup errors exit 2
mkdir -p "$WORK/other"
printf '[options]\naddons_path = ../custom\n' > "$WORK/other/odoo.conf"
run "$C" env
expect "two confs cover cwd" 2 '^SETUP ERROR: several confs cover' 'other/odoo\.conf'
rm -r "$WORK/other"
mkdir -p "$WORK/empty"
run "$WORK/empty" model sale.order
expect "nothing located" 2 '^SETUP ERROR: Odoo core not located' 'odoo\.json'
mkdir -p "$WORK/fakeroot/odoo" "$WORK/fakeroot/odoo/addons"
cp "$WORK/core/odoo/release.py" "$WORK/fakeroot/odoo/"
run "$WORK/empty" --odoo-root "$WORK/fakeroot" --addons "$C" model sale.order
expect "core without base" 2 'core not located: no root holds base/__manifest__\.py'

# real checkouts: the answers verified by hand against the 18.0 / 19.0 source
for R in "${ODOO_ROOT_18:-}" "${ODOO_ROOT_19:-}"; do
  [ -n "$R" ] || continue
  V=$(basename "$R")
  real() { run "$WORK/empty" --odoo-root "$R" --addons "$R/addons" "$@"; }
  real field sale.order access_url
  expect "$V sale.order.access_url" 0 '^VERDICT: FOUND via parent portal\.mixin$'
  real field sale.order delivery_date
  expect "$V sale.order.delivery_date" 1 '^VERDICT: NOT FOUND: .*commitment_date'
  real field event.type.booth partner_id
  expect "$V event.type.booth.partner_id" 1 '^note: partner_id is defined on event\.booth '
  real field event.booth booth_category_id
  expect "$V event.booth.booth_category_id" 0 '^VERDICT: FOUND via parent event\.type\.booth$'
  real field res.partner country_id
  expect "$V res.partner.country_id" 0 "base/models/res_partner\.py:[0-9]+ base \w+ via=self Many2one\('res\.country'\)"
  real field sale.order.line create_date
  expect "$V sale.order.line.create_date" 0 '^VERDICT: FOUND magic$'
  real field sale.report create_date
  expect "$V sale.report.create_date" 1 'sale_report\.py:[0-9]+ has _auto=False'
  real method sale.order _action_confirm
  expect "$V _action_confirm overrides" 0 'sale_stock/models/sale_order\.py:[0-9]+ sale_stock SaleOrder def _action_confirm' \
    'sale/models/sale_order\.py:[0-9]+ sale SaleOrder def _action_confirm\(self\) super=no'
  real method sale.order action_confirm
  expect "$V action_confirm calls _action_confirm" 0 'sale/models/sale_order\.py:[0-9]+ sale SaleOrder def action_confirm\(self\) super=no hooks: .*_action_confirm:[0-9]+'
  real method sale.order message_post
  expect "$V message_post base signature" 0 "mail/models/mail_thread\.py:[0-9]+ mail MailThread .*def message_post\(self, \*, body=''"
  real xmlid base.lang_vi_VN
  expect "$V base.lang_vi_VN" 0 'base/data/res\.lang\.csv:[0-9]+ base base\.lang_vi_VN$'
  real xmlid sales_team.group_sale_admin
  expect "$V group_sale_admin" 1 'closest in sales_team: .*group_sale_manager'
  real model event.type.booth
  expect "$V event.booth copies event.type.booth" 0 'copies event\.type\.booth into event\.booth: not event\.type\.booth'
  real model sale.order
  expect "$V sale.order extensions capped" 0 '^\+[0-9]+ more extensions \(--all lists them\) in: '
  real field stock.route name
  expect "$V stock.route.name in a file of several models" 0 'stock/models/stock_location\.py:[0-9]+ stock StockRoute via=self Char' \
    '^VERDICT: FOUND on stock\.route$'
  real field res.users email
  expect "$V res.users.email" 0 'base/models/res_users\.py:[0-9]+ base \w+ via=self Char related=.partner_id\.email.' \
    'via=_inherits res\.partner \(partner_id\) Char' '^VERDICT: FOUND on res\.users$'
  real field sale.order.line order_partner_id.country_id.code
  expect "$V related path" 0 '^VERDICT: FOUND .*: Many2one\(res\.partner\) > Many2one\(res\.country\) > Char$'
  real method res.country.state name_search
  expect "$V BaseModel method" 0 '^#1 .*base/models/res_country\.py:[0-9]+ base .*super=yes' '^#2 .*core BaseModel .*def name_search'
  real xmlid account.1_chart1111
  expect "$V chart template xmlid" 0 '^VERDICT: GENERATED account\.1_chart1111 at install: chart template row of l10n_vn '
  real xmlid l10n_vn.chart1111
  expect "$V chart template row is no xmlid" 1 'per company as account\.<company id>_chart1111'
done

echo "$passes checks passed, $fails failed"
[ "$fails" -eq 0 ]
