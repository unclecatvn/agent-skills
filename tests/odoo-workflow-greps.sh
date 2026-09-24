#!/usr/bin/env bash
# Runs the odoo-workflow Step 1 greps (V2, V3, W1, W2, C1) against a real Odoo checkout, with
# ROOTS from the bundled helper, and checks they surface evidence verified by hand. Needs Odoo
# source, so it is not part of `npm test`. Run it under both shells:
#   ODOO_ROOT=/path/to/odoo/18.0 bash tests/odoo-workflow-greps.sh
#   ODOO_ROOT=/path/to/odoo/18.0 zsh tests/odoo-workflow-greps.sh
# The Python-side trace (models, fields, methods, xmlids) is checked by tests/test_odoo_trace.sh.
set -u
HELPER="$(cd "$(dirname "$0")/.." && pwd)/skills/odoo-workflow/scripts/odoo_trace.py"
cd "${ODOO_ROOT:?set ODOO_ROOT to an Odoo checkout}" || exit 2
fails=0
check() { # name, output, extended regex the output must match
  if printf '%s\n' "$2" | grep -qE "$3"; then echo "ok   $1"; else echo "FAIL $1"; fails=$((fails + 1)); fi
}
refute() { # name, output, extended regex the output must not match
  if printf '%s\n' "$2" | grep -qE "$3"; then echo "FAIL $1"; fails=$((fails + 1)); else echo "ok   $1"; fi
}
roots() { python3 "$HELPER" --odoo-root "$ODOO_ROOT" --addons "$ODOO_ROOT/addons" roots 2>/dev/null; }
major=$(sed -nE 's/^version_info = \(([0-9]+),.*/\1/p' odoo/release.py)
echo "Odoo $major, shell ${ZSH_VERSION:+zsh }${BASH_VERSION:+bash}, $(roots | wc -l | tr -d ' ') roots"

check "roots include the core odoo/addons (base)" "$(roots)" '/odoo/addons$'

# V2: every view inheriting MODULE.VIEW, one-line and split inherit_id
v2() { # MODULE, VIEW
  grep -rnE -A1 --include='*.xml' "name=['\"]inherit_id['\"]|inherit_id=['\"]" $(roots) | grep -E ":[0-9]+:.*(ref|inherit_id)=['\"]($1\.)?$2['\"]|-[0-9]+-\s*ref=['\"]($1\.)?$2['\"]"
}
inherits=$(v2 sale view_order_form)
check "V2 finds sale_stock inheriting sale.view_order_form" "$inherits" 'sale_stock/views/sale_order_views\.xml'
check "V2 finds sale_margin inheriting sale.view_order_form" "$inherits" 'sale_margin/views/sale_order_views\.xml'
refute "V2 lists no view_order_form_* lookalike" "$inherits" 'view_order_form[a-z_]'
check "V2 finds a QWeb template with a single-quoted inherit_id" "$(v2 website_sale product)" "inherit_id='website_sale\.product'"
if [ "$major" = 18 ]; then split=mail_bot; else split=hr; fi
check "V2 finds the inherit_id split over two lines in mail_bot_hr" \
  "$(v2 $split res_users_view_form_preferences)" 'mail_bot_hr/views/res_users_views\.xml-[0-9]+-'

# V3: anchor nodes inside one record, absolute line numbers
f=addons/sale/views/sale_order_views.xml
range=$(grep -nE 'id="view_order_form"|</record>' "$f" | grep -A1 'id="view_order_form"' | cut -d: -f1 | tr '\n' ' ')
a=${range%% *}; b=$(echo "$range" | awk '{print $2}')
anchors=$(awk -v a="$a" -v b="$b" 'NR>=a && NR<=b && /name="partner_id"/ {print FILENAME":"NR": "$0}' "$f")
check "V3 finds partner_id in the sale form with absolute lines" "$anchors" "^$f:[0-9]{3,}: "
refute "V3: warehouse_id is not in the base sale form" \
  "$(awk -v a="$a" -v b="$b" 'NR>=a && NR<=b && /name="warehouse_id"/' "$f")" .
check "V2 + V3: warehouse_id comes from sale_stock" \
  "$(grep -nE 'name="warehouse_id"' addons/sale_stock/views/sale_order_views.xml)" .

# W1: OWL template definition and every t-inherit
w1=$(grep -rnE --include='*.xml' "t-name=['\"]web\.ControlPanel['\"]|t-inherit=['\"]web\.ControlPanel['\"]" $(roots))
check "W1 finds the web.ControlPanel definition" "$w1" 'web/static/src/search/control_panel/control_panel\.xml:[0-9]+:.*t-name="web\.ControlPanel"'
check "W1 finds a primary t-inherit of web.ControlPanel" "$w1" 't-inherit="web\.ControlPanel" t-inherit-mode="primary"'

# W2: JS class definition and its patches
w2=$(grep -rnE --include='*.js' "^export (default )?(class|function|const) ListRenderer[^A-Za-z0-9_]|patch\(\s*ListRenderer[^A-Za-z0-9_]" $(roots))
check "W2 finds the ListRenderer class" "$w2" 'web/static/src/views/list/list_renderer\.js:[0-9]+:export class ListRenderer '
check "W2 finds mail patching ListRenderer" "$w2" 'mail/static/src/views/web/list_renderer\.js:[0-9]+:patch\(ListRenderer\.prototype'

# C1: route (also split decorators) and controller subclasses (also multi-base and import aliases)
c1r() { grep -rnE --include='*.py' "@(http\.)?route\(.*['\"]$1['\"]|^\s*(route=)?\[?\s*['\"]$1['\"]" $(roots); }
c1c() { grep -rnE --include='*.py' "^class \w+\(([^)]*[ ,])?([A-Za-z_.]+\.)?$1[,)]|import.*[ ,]$1 as " $(roots); }
check "C1 finds the /shop/cart route" "$(c1r /shop/cart)" 'website_sale/controllers/(main|cart)\.py'
check "C1 finds a route whose decorator spans lines" \
  "$(c1r /sale/product_configurator/create_product)" 'sale/controllers/product_configurator\.py:[0-9]+:'
if [ "$major" = 18 ]; then
  c1=$(c1c WebsiteSale)
  check "C1 finds subclasses of WebsiteSale" "$c1" 'website_sale_loyalty/controllers/main\.py:[0-9]+:class WebsiteSale\(main\.WebsiteSale\)'
  check "C1 finds a multi-base subclass" "$c1" 'website_sale/controllers/combo_configurator\.py:[0-9]+:class '
  check "C1 finds an aliased import" "$c1" 'website_sale_mass_mailing/controllers/main\.py:[0-9]+:.*WebsiteSale as '
else
  check "C1 finds an aliased import of Cart" "$(c1c Cart)" 'website_sale_loyalty/controllers/cart\.py:[0-9]+:.*Cart as '
fi

echo "$fails failure(s)"
exit $((fails > 0))
