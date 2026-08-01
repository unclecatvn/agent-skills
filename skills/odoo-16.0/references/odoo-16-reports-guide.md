---
name: odoo-16-reports
description: Complete reference for Odoo 16 QWeb reports covering PDF/HTML/Text reports, report templates, paper formats, external/internal layouts, barcodes, translatable reports, multi-company, and custom fonts.
globs: "**/*.{py,xml}"
topics:
  - QWeb reports (qweb-pdf, qweb-html, qweb-text)
  - ir.actions.report fields
  - report.paperformat model
  - t-call layouts (web.external_layout, web.internal_layout)
  - Custom reports with _get_report_values
  - Translatable reports (t-lang)
  - Barcodes (/report/barcode route)
  - Multi-company and external_report_layout_id
  - Custom fonts in reports
when_to_use:
  - Creating PDF / HTML / text reports for models
  - Designing report templates with standard or custom layouts
  - Defining custom paper formats
  - Adding barcodes or QR codes to reports
  - Writing translatable reports
  - Adding custom fonts
---

# Odoo 16 Reports Guide

Complete reference for Odoo 16 QWeb reports: PDF, HTML, and text reports rendered through wkhtmltopdf or directly.

## Table of Contents

1. [Report Basics](#report-basics)
2. [`ir.actions.report` Fields](#iractionsreport-fields)
3. [Report Templates](#report-templates)
4. [Layouts (`t-call`)](#layouts-t-call)
5. [Paper Formats](#paper-formats)
6. [Custom Reports (`_get_report_values`)](#custom-reports-_get_report_values)
7. [Translatable Reports](#translatable-reports)
8. [Barcodes](#barcodes)
9. [Multi-Company Reports](#multi-company-reports)
10. [Custom Fonts](#custom-fonts)
11. [Debugging Reports](#debugging-reports)
12. [Quick Reference](#quick-reference)

---

## Report Basics

### What a QWeb Report Is

A QWeb report in Odoo 16 is the combination of:

1. An **`ir.actions.report` record** — the action that users trigger; configures the model, template, paper format, output type.
2. A **QWeb template** (`ir.ui.view`, usually declared with `<template id="...">`) — the HTML markup rendered for each record.
3. Optionally a Python **`AbstractModel`** named `report.<module>.<template_name>` whose `_get_report_values(docids, data)` feeds extra values to the template.

### Report Types (`report_type`)

| Value | Output | How |
|-------|--------|-----|
| `qweb-pdf` | PDF | Renders HTML + runs through `wkhtmltopdf` |
| `qweb-html` | HTML | Served directly (useful for previews and debugging) |
| `qweb-text` | Plain text | Renders QWeb and returns the text (used for POS tickets, email templates, etc.) |

Defined in `odoo/addons/base/models/ir_actions_report.py`:

```python
report_type = fields.Selection([
    ('qweb-html', 'HTML'),
    ('qweb-pdf', 'PDF'),
    ('qweb-text', 'Text'),
], required=True, default='qweb-pdf')
```

### Declaring a Report: The `<report>` Shortcut

The `<report>` tag expands to an `ir.actions.report` record. It does NOT create the template — you still write the `<template>` yourself.

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Action -->
    <report
        id="action_report_invoice"
        string="Invoice"
        model="account.move"
        report_type="qweb-pdf"
        name="my_module.report_invoice_document"
        file="my_module.report_invoice"
        print_report_name="'Invoice - %s' % (object.name or 'draft')"
        attachment="'Invoice-%s.pdf' % (object.name)"
        attachment_use="True"
    />

    <!-- Template (declared separately) -->
    <template id="report_invoice_document">
        <t t-call="web.html_container">
            <t t-foreach="docs" t-as="o">
                <t t-call="web.external_layout">
                    <div class="page">
                        <h2>Invoice <span t-field="o.name"/></h2>
                        <p>Partner: <span t-field="o.partner_id.name"/></p>
                        <p>Amount:
                            <span t-field="o.amount_total"
                                  t-options='{"widget": "monetary", "display_currency": o.currency_id}'/>
                        </p>
                    </div>
                </t>
            </t>
        </t>
    </template>
</odoo>
```

### Explicit Form (No Shortcut)

```xml
<record id="action_report_invoice" model="ir.actions.report">
    <field name="name">Invoice</field>
    <field name="model">account.move</field>
    <field name="report_type">qweb-pdf</field>
    <field name="report_name">my_module.report_invoice_document</field>
    <field name="report_file">my_module.report_invoice</field>
    <field name="binding_model_id" ref="account.model_account_move"/>
    <field name="binding_type">report</field>
    <field name="paperformat_id" ref="base.paperformat_euro"/>
</record>
```

### Menu / Print Menu Binding

Setting `binding_model_id` and `binding_type="report"` makes the action appear in that model's "Print" menu in the back-office UI.

---

## `ir.actions.report` Fields

All fields, verified from `odoo/addons/base/models/ir_actions_report.py`:

| Field | Type | Purpose |
|-------|------|---------|
| `name` | Char | Human-readable name (also shown in the Print menu) |
| `model` | Char | Target model name (e.g. `"account.move"`) — REQUIRED |
| `report_type` | Selection | `qweb-html` / `qweb-pdf` / `qweb-text` |
| `report_name` | Char | XML id of the QWeb template (`module.template`) — REQUIRED |
| `report_file` | Char | Hint for the main template file (optional) |
| `print_report_name` | Char | Python expression producing the download filename; has `object` (current record) and `time` in scope |
| `attachment` | Char | Python expression for an attachment filename; when set, the rendered PDF is saved as an `ir.attachment` on the record |
| `attachment_use` | Boolean | If True, reuse the stored attachment on subsequent prints (validated invoices, etc.) |
| `paperformat_id` | Many2one | `report.paperformat`; falls back to `company.paperformat_id`, then `base.paperformat_euro` |
| `groups_id` | Many2many | Groups allowed to run the report |
| `multi` | Boolean | If True, hide on single-record form views |
| `binding_model_id` / `binding_type` | — | Attach to a model's action menu |

### `attachment` vs `attachment_use`

Use both together to render-once, reprint-from-store:

```xml
<field name="attachment">'Invoice-%s.pdf' % object.name</field>
<field name="attachment_use" eval="True"/>
```

Only rendered reports with a filled `attachment` expression are stored (typically after the record reaches a non-draft state — check `print_report_name` vs `attachment` expressions in standard modules for inspiration).

### `print_report_name` Examples

```xml
<field name="print_report_name">'Invoice - %s' % (object.name or 'Draft')</field>
<field name="print_report_name">'SO-%s-%s' % (object.name, object.state)</field>
<field name="print_report_name">
    'BOM-%s-%s' % (object.product_tmpl_id.name or 'ref', time.strftime('%Y%m%d'))
</field>
```

Variables available: `object` (the current record) and `time` (the Python `time` module).

---

## Report Templates

### Minimal Skeleton

```xml
<template id="report_my_document">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="o">
            <t t-call="web.external_layout">
                <div class="page">
                    <!-- Your content -->
                    <h2 t-field="o.name"/>
                </div>
            </t>
        </t>
    </t>
</template>
```

Structure in words:

- `web.html_container` sets up `<html><head>` and includes report assets.
- `web.external_layout` wraps content with the company's header and footer.
- `div.page` is the per-page content (important for wkhtmltopdf page breaks).

### Variables Available in the Template

| Variable | Description |
|----------|-------------|
| `docs` | Recordset of the documents being rendered |
| `doc_ids` | List of IDs |
| `doc_model` | Model name string |
| `user` | `res.users` — the user printing the report |
| `res_company` | `res.company` — the user's current company |
| `company` | Automatically set by `web.external_layout` (multi-company aware) |
| `time` | Python `time` module |
| `context_timestamp` | Converts a UTC datetime to the user timezone |
| `web_base_url` | Base URL of the server |

Custom `_get_report_values` can add more (see below).

### Core QWeb Directives (Reports)

```xml
<!-- Loop -->
<t t-foreach="docs" t-as="o">
    ...
</t>

<!-- Condition -->
<p t-if="o.state == 'draft'">DRAFT</p>
<p t-elif="o.state == 'posted'">Posted</p>
<p t-else="">Other state</p>

<!-- Field rendering (smart: dates, currency, etc.) -->
<span t-field="o.date_order"/>
<span t-field="o.amount_total"
      t-options='{"widget": "monetary", "display_currency": o.currency_id}'/>

<!-- Escape a computed value -->
<span t-esc="o.name"/>
<span t-esc="'%s items' % len(o.line_ids)"/>

<!-- Raw (escape off) -->
<div t-out="o.note"/>

<!-- Call a template -->
<t t-call="web.external_layout">...</t>

<!-- Set a local var -->
<t t-set="subtotal" t-value="sum(l.price_subtotal for l in o.order_line)"/>

<!-- Attribute binding -->
<div t-att-class="'text-danger' if o.state == 'cancel' else 'text-success'"/>
<a t-attf-href="{{ web_base_url }}/web#id={{ o.id }}&amp;model={{ doc_model }}">Open</a>

<!-- Translation language (must be on t-call) -->
<t t-call="my_module.body" t-lang="o.partner_id.lang"/>
```

### `t-field` Widget Options

`t-options` passes a dict to the underlying field formatter:

```xml
<!-- Monetary -->
<span t-field="o.amount_total"
      t-options='{"widget": "monetary", "display_currency": o.currency_id}'/>

<!-- Date -->
<span t-field="o.date_order"
      t-options='{"format": "yyyy-MM-dd"}'/>

<!-- Image (binary field) -->
<img t-att-src="image_data_uri(o.image_1920)"/>

<!-- Selection (uses the label, not the key) -->
<span t-field="o.state"/>

<!-- Many2one (shows display_name) -->
<span t-field="o.partner_id"/>

<!-- HTML field -->
<div t-field="o.note"/>
```

---

## Layouts (`t-call`)

Odoo 16 provides several layout templates in `addons/web/views/report_templates.xml`:

| Template | Purpose |
|----------|---------|
| `web.html_container` | Top-level wrapper — always the first `t-call` |
| `web.external_layout` | Outer report layout — header, footer, company branding (chosen by `company.external_report_layout_id`) |
| `web.internal_layout` | Minimal layout for internal docs (no header/footer flourish) |
| `web.external_layout_standard` | The default standard layout |
| `web.external_layout_boxed`, `web.external_layout_bold`, `web.external_layout_striped` | Variants used when the company selects a different branding |
| `web.minimal_layout` | Used by the PDF pipeline internally (don't call from your templates) |

### Recipe: Report With Header/Footer

```xml
<template id="report_order_document">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="o">
            <t t-call="web.external_layout">
                <div class="page">
                    <h2>
                        Order <span t-field="o.name"/>
                    </h2>
                    <p>
                        <strong>Partner:</strong>
                        <span t-field="o.partner_id"/>
                    </p>
                    <table class="table table-sm o_main_table">
                        <thead>
                            <tr>
                                <th>Product</th>
                                <th class="text-end">Quantity</th>
                                <th class="text-end">Subtotal</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr t-foreach="o.order_line" t-as="line">
                                <td><span t-field="line.product_id"/></td>
                                <td class="text-end"><span t-field="line.product_uom_qty"/></td>
                                <td class="text-end">
                                    <span t-field="line.price_subtotal"
                                          t-options='{"widget": "monetary", "display_currency": o.currency_id}'/>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </t>
        </t>
    </t>
</template>
```

### Recipe: Internal Layout

```xml
<template id="report_internal_checklist">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="o">
            <t t-call="web.internal_layout">
                <div class="page">
                    <h3>Checklist: <t t-esc="o.name"/></h3>
                    <ul>
                        <li t-foreach="o.check_ids" t-as="c" t-esc="c.name"/>
                    </ul>
                </div>
            </t>
        </t>
    </t>
</template>
```

---

## Paper Formats

`report.paperformat` is a small model declared with these key fields (see `odoo/addons/base/data/report_paperformat_data.xml` for defaults):

| Field | Values / type | Notes |
|-------|---------------|-------|
| `name` | Char | Free-form label |
| `default` | Boolean | Whether listed as default when picking |
| `format` | Selection | `A0`..`A10`, `B0`..`B10`, `Letter`, `Legal`, `Tabloid`, `custom` |
| `page_height` / `page_width` | Integer (mm) | Only used when `format='custom'` |
| `orientation` | `Portrait` / `Landscape` | |
| `margin_top/bottom/left/right` | Integer (mm) | |
| `header_spacing` | Integer (mm) | Space reserved for header |
| `header_line` | Boolean | Draw a separator line under the header |
| `dpi` | Integer | Output DPI (default 90) |
| `disable_shrinking` | Boolean | Add wkhtmltopdf's `--disable-smart-shrinking` |

### Standard A4 Format (Odoo provides this)

From `odoo/addons/base/data/report_paperformat_data.xml`:

```xml
<record id="paperformat_euro" model="report.paperformat">
    <field name="name">A4</field>
    <field name="default" eval="True"/>
    <field name="format">A4</field>
    <field name="page_height">0</field>
    <field name="page_width">0</field>
    <field name="orientation">Portrait</field>
    <field name="margin_top">40</field>
    <field name="margin_bottom">32</field>
    <field name="margin_left">7</field>
    <field name="margin_right">7</field>
    <field name="header_line" eval="False"/>
    <field name="header_spacing">35</field>
    <field name="dpi">90</field>
</record>
```

Available XML IDs you can reference: `base.paperformat_euro` (A4), `base.paperformat_us` (Letter).

### Custom Paper Format

```xml
<record id="paperformat_shipping_label" model="report.paperformat">
    <field name="name">Shipping Label 100x150</field>
    <field name="default" eval="False"/>
    <field name="format">custom</field>
    <field name="page_height">150</field>
    <field name="page_width">100</field>
    <field name="orientation">Portrait</field>
    <field name="margin_top">2</field>
    <field name="margin_bottom">2</field>
    <field name="margin_left">2</field>
    <field name="margin_right">2</field>
    <field name="header_line" eval="False"/>
    <field name="header_spacing">2</field>
    <field name="dpi">200</field>
</record>
```

### Attaching a Paper Format to a Report

```xml
<record id="action_report_shipping_label" model="ir.actions.report">
    <field name="name">Shipping Label</field>
    <field name="model">stock.picking</field>
    <field name="report_type">qweb-pdf</field>
    <field name="report_name">my_module.report_shipping_label</field>
    <field name="paperformat_id" ref="my_module.paperformat_shipping_label"/>
</record>
```

Resolution order used by `ir.actions.report.get_paperformat()`:
1. `report.paperformat_id` on the action.
2. `env.company.paperformat_id`.
3. Fallback to `base.paperformat_euro`.

---

## Custom Reports (`_get_report_values`)

When you need more than `docs` (pre-computed totals, grouped data, related records fetched in bulk), define an `AbstractModel` named `report.<module>.<template_name>`.

```python
# my_module/report/report_invoice.py
from odoo import api, models


class ReportInvoice(models.AbstractModel):
    _name = 'report.my_module.report_invoice_document'
    _description = 'Invoice Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['account.move'].browse(docids)

        # Pre-compute everything you don't want to loop in QWeb
        totals_by_invoice = {
            move.id: {
                'line_count': len(move.invoice_line_ids),
                'subtotal': sum(l.price_subtotal for l in move.invoice_line_ids),
                'tax_total': move.amount_tax,
            }
            for move in docs
        }

        return {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'docs': docs,
            'data': data,
            'totals': totals_by_invoice,
        }
```

Register in `__init__.py`:

```python
# my_module/report/__init__.py
from . import report_invoice

# my_module/__init__.py
from . import report
```

Use the extra values in the template:

```xml
<template id="report_invoice_document">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="o">
            <t t-call="web.external_layout">
                <div class="page">
                    <h2>Invoice <span t-field="o.name"/></h2>
                    <p>Lines: <t t-esc="totals[o.id]['line_count']"/></p>
                    <p>Subtotal:
                        <span t-esc="totals[o.id]['subtotal']"
                              t-options='{"widget": "monetary", "display_currency": o.currency_id}'/>
                    </p>
                </div>
            </t>
        </t>
    </t>
</template>
```

Important: the AbstractModel name MUST be `report.<report_name>` where `<report_name>` matches the `report_name` field on `ir.actions.report`.

---

## Translatable Reports

`t-lang` switches the translation context for a `t-call` — it is the ONLY supported way to render part of a report in another language.

### Two-Template Pattern (Standard)

```xml
<!-- Wrapper: loops, delegates to the document template per language -->
<template id="report_saleorder">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="o">
            <t t-call="my_module.report_saleorder_document" t-lang="o.partner_id.lang or user.lang"/>
        </t>
    </t>
</template>

<!-- Document: rendered in the requested language -->
<template id="report_saleorder_document">
    <!-- Re-browse in the target language so translatable fields follow -->
    <t t-set="o" t-value="o.with_context(lang=o.partner_id.lang)"/>
    <t t-call="web.external_layout">
        <div class="page">
            <h2>Order <span t-field="o.name"/></h2>
            <p>Status: <span t-field="o.state"/></p>  <!-- translated Selection label -->
        </div>
    </t>
</template>
```

Key rules:

- `t-lang="<python expr>"` only works on a `t-call`.
- Use `o.with_context(lang=...)` to re-browse the record so that translatable Char/Text/Selection values render in the right language.
- Terms inside the template (static strings) must be extracted into `.po` files like any other module content.

### Header/Footer in a Different Language

The wkhtmltopdf rendering pipeline sets `t-lang` on the `web.external_layout` call itself in some patterns — you can force the header and footer into a fixed language (e.g. English) while keeping the body in the partner's language:

```xml
<template id="report_invoice">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="o">
            <t t-call="web.external_layout" t-lang="'en_US'">
                <div class="page">
                    <!-- Re-browse body content in the partner's language -->
                    <t t-set="o" t-value="o.with_context(lang=o.partner_id.lang)"/>
                    <h2>Invoice <span t-field="o.name"/></h2>
                </div>
            </t>
        </t>
    </t>
</template>
```

---

## Barcodes

Odoo serves barcode images through the controller route registered in `addons/web/controllers/report.py`:

```python
@http.route(['/report/barcode', '/report/barcode/<barcode_type>/<path:value>'],
            type='http', auth="public")
def report_barcode(self, barcode_type, value, **kwargs):
    ...
```

So there are two valid URL shapes in Odoo 16.

### Short Path Form (`/report/barcode/<type>/<value>`)

```xml
<!-- QR code -->
<img t-att-src="'/report/barcode/QR/%s' % o.name"/>

<!-- Code128 -->
<img t-att-src="'/report/barcode/Code128/%s' % o.default_code"/>
```

### Query-String Form (Supports Sizing, Human-Readable Labels)

```xml
<img t-att-src="'/report/barcode/?barcode_type=%s&amp;value=%s&amp;width=%s&amp;height=%s' % (
    'Code128', o.name, 200, 50
)"/>

<img t-att-src="'/report/barcode/?barcode_type=%s&amp;value=%s&amp;width=%s&amp;height=%s&amp;humanreadable=1' % (
    'EAN13', o.barcode or '0000000000000', 300, 100
)"/>
```

In XML, remember to escape `&` as `&amp;`.

### Supported Barcode Types (Odoo 16)

From `ir.actions.report.barcode()`:

- Linear: `Codabar`, `Code11`, `Code128`, `Code39`, `Extended39`, `Extended93`, `Standard39`, `Standard93`, `EAN8`, `EAN13`, `FIM`, `I2of5`, `ISBN`, `MSI`, `POSTNET`, `UPCA`, `USPS_4State`
- 2D: `QR`, `DataMatrix`
- Heuristic: `auto` (guesses from value length: 8 → EAN8, 13 → EAN13, else Code128)

### Parameters (query string)

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `barcode_type` | string | — | One of the types above |
| `value` | string | — | The data to encode |
| `width` | int | 600 | Pixel width |
| `height` | int | 100 | Pixel height |
| `humanreadable` | 0 / 1 | 0 | Adds readable text under barcode |
| `quiet` | 0 / 1 | 1 | White margins on sides |
| `mask` | string | None | Mask for QR bills (e.g. Swiss QR) |
| `barBorder` | int | 4 | QR border size |
| `barLevel` | `L` / `M` / `Q` / `H` | `L` | QR error correction level |

### Product-Barcode Recipe

```xml
<template id="report_product_label">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="p">
            <t t-call="web.external_layout">
                <div class="page">
                    <h3 t-field="p.name"/>
                    <p>Ref: <span t-field="p.default_code"/></p>
                    <img t-att-src="'/report/barcode/?barcode_type=%s&amp;value=%s&amp;width=%s&amp;height=%s&amp;humanreadable=1' % (
                        'Code128',
                        p.default_code or p.barcode or str(p.id),
                        300, 80,
                    )"/>
                </div>
            </t>
        </t>
    </t>
</template>
```

---

## Multi-Company Reports

`web.external_layout` handles multi-company automatically:

1. Prefer an explicit `company` variable (if your template sets one).
2. Else the `company_id` passed through the render context.
3. Else `o.company_id` if the current document has one.
4. Else `res_company` (the user's active company).

The layout variant used is read from `company.external_report_layout_id` (Standard, Boxed, Bold, Striped, Clean, etc.).

For reports spanning documents from several companies, set `company` yourself inside the loop:

```xml
<template id="report_cross_company">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="o">
            <t t-set="company" t-value="o.company_id or res_company"/>
            <t t-call="web.external_layout">
                <div class="page">
                    <h2 t-field="o.name"/>
                    <p>From company: <span t-field="company.name"/></p>
                </div>
            </t>
        </t>
    </t>
</template>
```

---

## Custom Fonts

To ship a custom font used by PDF reports:

1. Drop the font files under `my_module/static/src/fonts/`.
2. Declare them in `web.report_assets_common` (NOT `web.assets_backend`).
3. Reference the font in QWeb or CSS.

`my_module/static/src/scss/report_fonts.scss`:

```scss
@font-face {
    font-family: "Inter";
    src: url("/my_module/static/src/fonts/Inter-Regular.woff2") format("woff2");
    font-weight: 400;
}
@font-face {
    font-family: "Inter";
    src: url("/my_module/static/src/fonts/Inter-Bold.woff2") format("woff2");
    font-weight: 700;
}

.o_invoice_title {
    font-family: "Inter", sans-serif;
    font-weight: 700;
    font-size: 28px;
}
```

`my_module/__manifest__.py`:

```python
'assets': {
    'web.report_assets_common': [
        'my_module/static/src/scss/report_fonts.scss',
    ],
},
```

Use in a template:

```xml
<h1 class="o_invoice_title">Invoice <span t-field="o.name"/></h1>
```

Only SCSS/CSS included in `web.report_assets_common` is available to the PDF renderer; `web.assets_backend` is only loaded in the back-office UI.

---

## Debugging Reports

### Preview the HTML

With developer mode on, you can open:

```
/report/html/<report_name>/<doc_id>
```

For example:

```
/report/html/my_module.report_invoice_document/42
```

The HTML is rendered exactly as wkhtmltopdf will see it. Missing header/footer is expected here — they are injected by the PDF pipeline.

### Preview the PDF

```
/report/pdf/<report_name>/<doc_id>
```

### Text Output

```
/report/text/<report_name>/<doc_id>
```

(Only meaningful for `report_type='qweb-text'`.)

### Download Filename

`print_report_name` controls the filename you see on download. It is a Python expression — double-check you escaped quotes in XML (`&apos;`, `&quot;`) when the expression uses them.

### Common Pitfalls

- **Blank PDF**: forgotten `web.html_container` wrapper, or the `web.external_layout` doesn't wrap a `div.page`.
- **Styles missing in PDF**: SCSS added to `web.assets_backend` instead of `web.report_assets_common`.
- **Report template not found**: `report_name` on the action doesn't match the `<template id="...">` (include module prefix).
- **`object` undefined in `print_report_name`**: the expression is eval'd with `object` (single record) and `time`. Not `obj`, not `record`.
- **Wkhtmltopdf too old**: Odoo 16 needs 0.12.x. Server log complains on startup if unsuitable.

---

## Quick Reference

### Minimal Module Layout

```
my_module/
├── __manifest__.py
├── __init__.py
├── models/
│   └── ...
├── report/
│   ├── __init__.py
│   ├── report_invoice.py              # AbstractModel (optional)
│   ├── report_invoice_templates.xml   # <report> and <template>
│   └── paperformat_data.xml           # Custom report.paperformat (optional)
└── static/src/
    ├── scss/
    │   └── report_fonts.scss
    └── fonts/
        └── Inter-Regular.woff2
```

`__manifest__.py`:

```python
{
    'name': 'My Module',
    'version': '16.0.1.0.0',
    'author': 'UncleCat',
    'license': 'LGPL-3',
    'depends': ['base', 'web'],
    'data': [
        'report/paperformat_data.xml',
        'report/report_invoice_templates.xml',
    ],
    'assets': {
        'web.report_assets_common': [
            'my_module/static/src/scss/report_fonts.scss',
        ],
    },
}
```

### Report Action (Full Form)

```xml
<report
    id="action_report_my_doc"
    string="My Document"
    model="my.model"
    report_type="qweb-pdf"
    name="my_module.report_my_doc_document"
    file="my_module.report_my_doc"
    print_report_name="'MyDoc-%s' % (object.name or 'draft')"
    attachment="'MyDoc-%s.pdf' % object.name"
    attachment_use="True"
    paperformat_id="base.paperformat_euro"
    groups_id="base.group_user"
    binding_model_id="model_my_model"
    binding_type="report"
/>
```

### Template Skeleton

```xml
<template id="report_my_doc_document">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="o">
            <t t-call="web.external_layout">
                <div class="page">
                    <!-- Your content -->
                </div>
            </t>
        </t>
    </t>
</template>
```

### Useful URLs

| URL | Description |
|-----|-------------|
| `/report/html/<report_name>/<id>` | Render HTML preview |
| `/report/pdf/<report_name>/<id>` | Download PDF |
| `/report/text/<report_name>/<id>` | Text output |
| `/report/barcode/<type>/<value>` | Barcode PNG (short form) |
| `/report/barcode/?barcode_type=...&value=...&width=...&height=...&humanreadable=1` | Barcode PNG with options |

### QWeb Cheat Sheet

| Directive | Usage |
|-----------|-------|
| `t-call="web.html_container"` | Report wrapper (mandatory) |
| `t-call="web.external_layout"` | Header + footer + branding |
| `t-call="web.internal_layout"` | Minimal layout |
| `t-foreach="docs" t-as="o"` | Iterate records |
| `t-if / t-elif / t-else` | Conditionals |
| `t-field="o.field"` | Smart render (formats dates, currencies, images) |
| `t-esc="expr"` | Escape + render |
| `t-out="expr"` | Escape-safe HTML render: outputs the raw string only when the value is a `markupsafe.Markup` instance, otherwise HTML-escapes like `t-esc`. Safe default for HTML fields (their values are already wrapped in `Markup`). Never feed it user input wrapped in `Markup` without sanitising first. |
| `t-set="x" t-value="..."` | Local variable |
| `t-options='{"widget": "monetary", "display_currency": o.currency_id}'` | Field widget options |
| `t-lang="'en_US'"` | Translation language (on `t-call` only) |
| `t-attf-href="{{ web_base_url }}/..."` | Templated attribute |

---

## Coding Conventions

- Keep printable report actions and paper formats in `<model>_reports.xml` and
  QWeb report templates in `<model>_templates.xml`.
- Keep SQL-view report Python and backend views together as
  `<model>_report.py` and `<model>_report_views.xml`.
- Use stable, descriptive XML IDs and record names; avoid generic report IDs
  that become unclear when several reports share a module.

## Base Code Reference

The APIs and templates documented here live in the Odoo 16 source:

- `odoo/addons/base/models/ir_actions_report.py` — `ir.actions.report` model, `_render_qweb_pdf`, `_render_qweb_html`, `_render_qweb_text`, `barcode`, `get_paperformat`.
- `odoo/addons/base/data/report_paperformat_data.xml` — default paper formats (`paperformat_euro`, `paperformat_us`, `paperformat_batch_deposit`).
- `addons/web/views/report_templates.xml` — `web.html_container`, `web.external_layout`, `web.internal_layout`, `web.minimal_layout`, `web.external_layout_standard`, and the other branding variants.
- `addons/web/controllers/report.py` — `/report/html/...`, `/report/pdf/...`, `/report/text/...`, `/report/barcode/...`, `/report/download`.
