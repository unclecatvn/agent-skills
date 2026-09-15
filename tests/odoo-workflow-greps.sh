#!/usr/bin/env bash
# Runs the odoo-workflow Step 1 commands against a real Odoo checkout and checks they surface
# evidence verified by hand. Needs Odoo source, so it is not part of `npm test`.
#   ODOO_ROOT=/path/to/odoo/18.0 tests/odoo-workflow-greps.sh
set -u
cd "${ODOO_ROOT:?set ODOO_ROOT to an Odoo checkout}" || exit 2
ROOTS="addons odoo/addons"
fails=0
check() { # name, output, extended regex the output must match
  if printf '%s\n' "$2" | grep -qE "$3"; then echo "ok   $1"; else echo "FAIL $1"; fails=$((fails + 1)); fi
}
refute() { # name, output, extended regex the output must not match
  if printf '%s\n' "$2" | grep -qE "$3"; then echo "FAIL $1"; fails=$((fails + 1)); else echo "ok   $1"; fi
}
extensions() { # MODEL (regex-escaped): commands 1-3, file paths only
  { grep -rnE --include='*.py' "_name\s*=\s*([A-Za-z_]+\s*=\s*)?['\"]$1['\"]" $ROOTS
    grep -rnE --include='*.py' "_inherit\s*=.*['\"]$1['\"]" $ROOTS
    grep -rnE --include='*.py' -A12 "_inherit\s*=\s*[[(][^])]*$" $ROOTS | grep -E "['\"]$1['\"]"
  } | sed -E 's/^([^:]+\.py)[-:][0-9]+[-:].*/\1/' | sort -u
}
field() { # FIELD, MODEL_FILES...: command 5
  local f=$1; shift
  grep -nE "^\s+$f(\s*:\s*[A-Za-z_.]+)?\s*=\s*fields\." "$@" /dev/null
}

echo "Odoo $(grep -m1 '^version_info' odoo/release.py)"

chained=$(grep -rhoE --include='*.py' "^\s+_name\s*=\s*[A-Za-z_]+\s*=\s*['\"][a-z_.]+['\"]" $ROOTS | head -1 | sed -E "s/.*['\"]([a-z_.]+)['\"]/\1/")
check "command 1 finds a chained _name ($chained)" \
  "$(grep -rnE --include='*.py' "_name\s*=\s*([A-Za-z_]+\s*=\s*)?['\"]${chained//./\\.}['\"]" $ROOTS)" .

mail=$(extensions 'mail\.thread')
check "command 3 finds the multi-line _inherit in account_journal.py" "$mail" 'account/models/account_journal\.py'

partner=$(extensions 'res\.partner')
check "command 5 finds annotated res.partner.country_id" \
  "$(field country_id $partner)" 'base/models/res_partner\.py:[0-9]+:\s+country_id: '

so=$(extensions 'sale\.order')
refute "command 5 finds no delivery_date on sale.order" "$(field delivery_date $so)" .
check "command 5 finds commitment_date on sale.order" "$(field commitment_date $so)" 'sale/models/sale_order\.py'
check "command 5 finds both qty_delivered_method definitions" \
  "$(field qty_delivered_method $(extensions 'sale\.order\.line'))" 'sale_stock/models/sale_order_line\.py'

start=$(grep -nE "^\s+def action_confirm\(" addons/sale/models/sale_order.py | cut -d: -f1)
check "command 7 finds the _action_confirm hook" \
  "$(sed -n "${start},$((start + 40))p" addons/sale/models/sale_order.py | grep -nE "\._[a-z_]+\(")" '\._action_confirm\('

view_inheritors() { # MODULE, VIEW: command 9
  grep -rnE --include='*.xml' "name=['\"]inherit_id['\"] ref=['\"]($1\.)?$2['\"]|inherit_id=['\"]($1\.)?$2['\"]" $ROOTS
}
inherits=$(view_inheritors sale view_order_form)
check "command 9 finds sale_stock inheriting sale.view_order_form" "$inherits" 'sale_stock/views/sale_order_views\.xml'
check "command 9 finds sale_margin inheriting sale.view_order_form" "$inherits" 'sale_margin/views/sale_order_views\.xml'
check "command 9 finds a QWeb template with a single-quoted inherit_id" \
  "$(view_inheritors website_sale product)" "inherit_id='website_sale\.product'"

refute "command 10: warehouse_id is not in the base sale views" \
  "$(grep -nE 'name="warehouse_id"' addons/sale/views/sale_order_views.xml)" .
check "command 10: warehouse_id comes from sale_stock" \
  "$(grep -nE 'name="warehouse_id"' addons/sale_stock/views/sale_order_views.xml)" .

refute "group_sale_admin does not exist" "$(grep -rn --include='*.xml' 'id="group_sale_admin"' $ROOTS)" .
check "group_sale_manager exists" "$(grep -rn --include='*.xml' 'id="group_sale_manager"' $ROOTS)" 'sales_team/security'

echo "$fails failure(s)"
exit $((fails > 0))
