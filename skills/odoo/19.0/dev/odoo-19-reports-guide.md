# Odoo 19 Reports Guide

Guide for creating QWeb reports in Odoo 19: PDF/HTML reports, templates, and paper formats.

## Table of Contents
- [Report Basics](#report-basics)
- [Report Declaration](#report-declaration)
- [Report Templates](#report-templates)
- [Custom Reports](#custom-reports)
- [Paper Formats](#paper-formats)
- [Translatable Reports](#translatable-reports)
- [Barcodes](#barcodes)

---

## Report Basics

Reports are written in HTML/QWeb. PDF rendering is performed by wkhtmltopdf.

Reports consist of:
1. A **report action** (`ir.actions.report`)
2. A **QWeb template** for the report content

---

## Report Declaration

### Using report Tag (Simple)

```xml
<report
    id="account_invoice_report"
    string="Invoice"
    model="account.move"
    report_type="qweb-pdf"
    name="account.report_invoice"
    file="account.report_invoice"
    print_report_name="'Invoice - %s' % (object.name)"
/>
```

### Using record Tag (Advanced)

```xml
<record id="my_report" model="ir.actions.report">
    <field name="name">My Report</field>
    <field name="model">my.model</field>
    <field name="report_type">qweb-pdf</field>
    <field name="report_name">my_module.my_template</field>
    <field name="print_report_name">'My Report - %s' % (object.name)</field>
    <field name="binding_model_id" ref="model_my_model"/>
    <field name="paperformat_id" ref="paperformat_euro"/>
</record>
```

### Report Attributes

| Attribute | Description |
|-----------|-------------|
| `id` | External identifier |
| `string` | Report name |
| `model` | Model for the report |
| `report_type` | `qweb-pdf` or `qweb-html` |
| `name` | External ID of QWeb template |
| `file` | Same as name (for backward compatibility) |
| `print_report_name` | Python expression for filename |
| `paperformat_id` | Paper format |
| `binding_model_id` | Model to show in Print menu |
| `groups_id` | Groups allowed to use report |
| `multi` | If True, don't show on form view |
| `attachment_use` | Generate once, reprint from stored |
| `attachment` | Python expression for attachment |

---

## Report Templates

### Template Variables

Report templates always have access to:

| Variable | Description |
|----------|-------------|
| `docs` | Records for the current report |
| `doc_ids` | List of ids for `docs` |
| `doc_model` | Model name for `docs` |
| `time` | Python `time` module |
| `user` | User printing the report |
| `res_company` | Current user's company |
| `website` | Current website (if any) |
| `web_base_url` | Base URL for webserver |
| `context_timestamp` | Function to convert datetime to user timezone |

### Minimal Template

```xml
<template id="report_invoice">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="o">
            <t t-call="web.external_layout">
                <div class="page">
                    <h2>Invoice</h2>
                    <p>Customer: <span t-field="o.partner_id.name"/></p>
                    <p>Total: <span t-field="o.amount_total"/></p>
                </div>
            </t>
        </t>
    </t>
</template>
```

### External Layout

Calling `web.external_layout` adds default header and footer.

```xml
<t t-call="web.external_layout">
    <div class="page">
        <!-- Your content here -->
    </div>
</t>
```

#### Layout Variants

| Layout | Description |
|--------|-------------|
| `web.external_layout` | Standard layout (with header/footer) |
| `web.external_layout_background` | With background |
| `web.external_layout_clean` | Clean layout (minimal) |
| `web.external_layout_boxed` | Boxed layout |

---

## Custom Reports

For custom reports, create a report class that overrides `_get_report_values`:

```python
from odoo import models

class MyReport(models.AbstractModel):
    _name = 'report.my_module.my_template'
    _description = 'My Custom Report'

    def _get_report_values(self, docids, data=None):
        docs = self.env['my.model'].browse(docids)

        return {
            'doc_ids': docids,
            'doc_model': 'my.model',
            'docs': docs,
            'data': data,
            'my_custom_value': self._compute_custom(docs),
        }

    def _compute_custom(self, docs):
        # Custom computation
        return sum(doc.amount for doc in docs)
```

Use custom values in template:

```xml
<template id="my_template">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="o">
            <t t-call="web.external_layout">
                <div class="page">
                    <h2>My Report</h2>
                    <p>Total: <span t-esc="my_custom_value"/></p>
                </div>
            </t>
        </t>
    </t>
</template>
```

---

## Paper Formats

### Built-in Paper Formats

| Format | Size |
|--------|------|
| `paperformat_euro` | A4 |
| `paperformat_us` | Letter |
| `paperformat_us_legal` | Legal |

### Custom Paper Format

```xml
<record id="paperformat_my_format" model="report.paperformat">
    <field name="name">My Custom Format</field>
    <field name="default" eval="True"/>
    <field name="format">A4</field>
    <field name="page_height">297</field>
    <field name="page_width">210</field>
    <field name="orientation">Portrait</field>
    <field name="margin_top">40</field>
    <field name="margin_bottom">20</field>
    <field name="margin_left">7</field>
    <field name="margin_right">7</field>
    <field name="header_line" eval="False"/>
    <field name="header_spacing">35</field>
    <field name="dpi">90</field>
</record>
```

### Format Attributes

| Attribute | Description |
|-----------|-------------|
| `format` | Paper size (A4, Letter, etc.) or Custom |
| `page_height` | Page height in mm |
| `page_width` | Page width in mm |
| `orientation` | Portrait or Landscape |
| `margin_top` | Top margin in mm |
| `margin_bottom` | Bottom margin in mm |
| `margin_left` | Left margin in mm |
| `margin_right` | Right margin in mm |
| `header_line` | Show header line |
| `header_spacing` | Header spacing in mm |
| `dpi` | Resolution (default: 90) |

---

## Translatable Reports

### Two-Template Approach

1. Main template (wrapper)
2. Translatable document template

```xml
<!-- Main template -->
<template id="report_saleorder">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="doc">
            <t t-call="sale.report_saleorder_document" t-lang="doc.partner_id.lang"/>
        </t>
    </t>
</template>

<!-- Translatable template -->
<template id="report_saleorder_document">
    <!-- Re-browse with partner language -->
    <t t-set="doc" t-value="doc.with_context(lang=doc.partner_id.lang)" />
    <t t-call="web.external_layout">
        <div class="page">
            <div class="row">
                <div class="col-6">
                    <strong>Invoice address:</strong>
                    <div t-field="doc.partner_invoice_id" t-options='{"widget": "contact", "no_marker": True}'/>
                </div>
            </div>
        </div>
    </t>
</template>
```

### Language Attribute

Use `t-lang` to set language for a template section:

```xml
<t t-call="my.template" t-lang="fr_FR">
    <!-- Will be rendered in French -->
</t>

<t t-call="my.template" t-lang="doc.partner_id.lang">
    <!-- Will be rendered in partner's language -->
</t>
```

**Note**: Works only with `t-call`, not on regular XML nodes.

---

## Barcodes

### Embed Barcode

```xml
<img t-att-src="'/report/barcode/?type=%s&amp;value=%s&amp;width=%s&amp;height=%s' % ('QR', o.name, 200, 200)"/>
```

### Barcode Controller Parameters

| Parameter | Values |
|-----------|--------|
| `type` | `QR`, `Code128`, `EAN13`, `EAN8`, `UPCA`, `UPCE` |
| `value` | Barcode value |
| `width` | Width in pixels |
| `height` | Height in pixels |
| `humanreadable` | `1` or `0` (show text below) |

### Example

```xml
<div class="page">
    <h2>Product: <span t-field="o.name"/></h2>
    <img
        t-att-src="'/report/barcode/?type=%s&amp;value=%s&amp;width=%s&amp;height=%s&amp;humanreadable=1' % ('EAN13', o.barcode, 600, 100)"
        alt="Barcode"/>
</div>
```

---

## QWeb Tips

### Directives

| Directive | Description |
|-----------|-------------|
| `t-esc` | Escape and output value |
| `t-raw` | Output without escaping (XSS risk) |
| `t-field` | Output field value (formatted) |
| `t-if` | Conditional display |
| `t-elif` | Else if condition |
| `t-else` | Else condition |
| `t-foreach` | Loop over collection |
| `t-as` | Variable name for foreach |
| `t-set` | Set variable |
| `t-call` | Call another template |
| `t-lang` | Set language for template |

### t-field Options

```xml
<span t-field="o.date" t-options='{"widget": "date"}'/>
<span t-field="o.amount" t-options='{"widget": "monetary", "display_currency": o.currency_id}'/>
<div t-field="o.partner_id" t-options='{"widget": "contact", "no_marker": True}'/>
```

---

## References

- Source: Odoo 19 documentation `/doc/developer/reference/backend/reports.rst`
