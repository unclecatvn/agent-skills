---
name: odoo-18-reports
description: Complete reference for Odoo 18 QWeb reports covering PDF/HTML reports, report templates, paper formats, custom reports, custom fonts, translatable templates, barcodes, and report actions.
globs: "**/*.{py,xml}"
topics:
  - QWeb reports (qweb-pdf, qweb-html)
  - Report templates and layouts
  - Paper formats (report.paperformat)
  - Custom reports with _get_report_values
  - Translatable reports (t-lang)
  - Barcodes in reports
  - Custom fonts for reports
  - Report actions and bindings
when_to_use:
  - Creating PDF reports for models
  - Designing report templates
  - Adding custom fonts to reports
  - Creating translatable reports
  - Implementing barcode support
  - Customizing report rendering
---

# Odoo 18 Reports Guide

Complete reference for Odoo 18 QWeb reports: PDF/HTML reports, templates, paper formats, and custom reports.

## Table of Contents

1. [Report Basics](#report-basics)
2. [Report Templates](#report-templates)
3. [Report Actions](#report-actions)
4. [Paper Formats](#paper-formats)
5. [Custom Reports](#custom-reports)
6. [Translatable Reports](#translatable-reports)
7. [Barcodes](#barcodes)
8. [Custom Fonts](#custom-fonts)

---

## Report Basics

### QWeb Reports

Reports in Odoo are written in HTML/QWeb and rendered to PDF using `wkhtmltopdf`.

#### Report Types

| Type | Description |
|------|-------------|
| `qweb-pdf` | PDF report (most common) |
| `qweb-html` | HTML report (for web viewing) |

### Report Declaration

```xml
<report
    id="account_invoices"
    model="account.move"
    string="Invoices"
    report_type="qweb-pdf"
    name="account.report_invoice"
    file="account_report_invoice"
    print_report_name="'Invoice-{}-{}'.format(object.number or 'n/a', object.state)"
/>
```

### Report Attributes

| Attribute | Type | Description | Required |
|-----------|------|-------------|----------|
| `id` | string | Unique identifier (external ID) | Yes |
| `model` | string | Model to report on | Yes |
| `string` / `name` | string | Human-readable name | Yes |
| `report_type` | string | `qweb-pdf` or `qweb-html` | No (default: qweb-pdf) |
| `name` | string | External ID of QWeb template | Yes |
| `file` | string | Output file name pattern | No |
| `print_report_name` | string | Python expression for file name | No |
| `groups_id` | Many2many | Groups allowed to view/use | No |
| `multi` | boolean | Don't show on form view if True | No |
| `paperformat_id` | Many2one | Paper format to use | No |
| `attachment_use` | boolean | Generate once, reprint stored | No |
| `attachment` | string | Python expression for attachment name | No |
| `binding_model_id` | Many2one | Model to bind action to | No |

### Report Action vs Record

The `<report>` tag creates two records:

1. **ir.actions.report** - The report action
2. **ir.ui.view** - The QWeb template

```xml
<!-- Shortcut: creates both records -->
<report
    id="my_report"
    model="my.model"
    name="my_module.my_report_template"
    report_type="qweb-pdf"
/>

<!-- Equivalent to: -->
<record id="my_report" model="ir.actions.report">
    <field name="name">My Report</field>
    <field name="model">my.model</field>
    <field name="report_name">my_module.my_report_template</field>
    <field name="report_type">qweb-pdf</field>
</record>

<template id="my_report_template">
    <!-- Template content -->
</template>
```

---

## Report Templates

### Minimal Template

```xml
<template id="report_invoice">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="o">
            <t t-call="web.external_layout">
                <div class="page">
                    <h2>Invoice</h2>
                    <p>Invoice Number: <span t-field="o.name"/></p>
                    <p>Amount: <span t-field="o.amount_total"/></p>
                </div>
            </t>
        </t>
    </t>
</template>
```

### Template Structure

```
web.html_container
    └── web.external_layout (header + footer)
            └── div.page (your content)
```

### Available Variables

| Variable | Description |
|----------|-------------|
| `docs` | Records for the report (recordset) |
| `doc_ids` | List of IDs for `docs` |
| `doc_model` | Model name for `docs` |
| `time` | Python `time` module |
| `user` | Current user (res.user) |
| `res_company` | Current user's company |
| `website` | Current website (if any) |
| `web_base_url` | Base URL for webserver |
| `context_timestamp` | Function to convert datetime to user timezone |

### Using Variables

```xml
<template id="my_report">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="o">
            <t t-call="web.external_layout">
                <div class="page">
                    <!-- Standard fields -->
                    <p t-field="o.name"/>
                    <p t-field="o.partner_id.name"/>

                    <!-- User info -->
                    <p>Printed by: <span t-field="user.name"/></p>

                    <!-- Company info -->
                    <p>Company: <span t-field="res_company.name"/></p>

                    <!-- Time -->
                    <p>Printed at: <span t-esc="time.strftime('%Y-%m-%d %H:%M')"/></p>

                    <!-- Context timestamp (converts to user timezone) -->
                    <p>Invoice date: <span t-esc="context_timestamp(o.invoice_date)"/></p>
                </div>
            </t>
        </t>
    </t>
</template>
```

### QWeb Directives

```xml
<!-- t-foreach: Loop -->
<t t-foreach="docs" t-as="doc">
    <p t-field="doc.name"/>
</t>

<!-- t-if: Condition -->
<p t-if="doc.state == 'draft'">Draft Document</p>

<!-- t-esc: Escape and render -->
<p t-esc="doc.description"/>

<!-- t-field: Smart rendering (dates, currencies, etc.) -->
<span t-field="o.date_order"/>  <!-- Formatted date -->
<span t-field="o.amount_total"/>  <!-- Formatted currency -->

<!-- t-call: Include another template -->
<t t-call="web.external_layout"/>

<!-- t-set: Set variable -->
<t t-set="total" t-value="sum(line.price_unit * line.quantity for line in o.line_ids)"/>

<!-- t-att: Set attribute -->
<a t-attf-href="https://example.com/invoice/{{o.id}}">View</a>
```

### Direct Attributes in Odoo 18

```xml
<!-- OLD (deprecated) -->
<div t-attf-class="{'alert-danger': o.state == 'error'}"/>

<!-- NEW (Odoo 18) -->
<div class="alert-danger" t-if="o.state == 'error'"/>
```

---

## Report Actions

### Basic Report Action

```xml
<record id="report_my_report" model="ir.actions.report">
    <field name="name">My Report</field>
    <field name="model">my.model</field>
    <field name="report_type">qweb-pdf</field>
    <field name="report_name">my_module.my_report_template</field>
</record>
```

### Report with Dynamic Filename

```xml
<record id="report_invoice" model="ir.actions.report">
    <field name="name">Invoice</field>
    <field name="model">account.move</field>
    <field name="report_type">qweb-pdf</field>
    <field name="report_name">account.report_invoice</field>
    <field name="print_report_name">
        'Invoice-{}-{}'.format(
            object.number or 'n/a',
            object.state
        )
    </field>
</record>
```

### Report with Attachment

```xml
<record id="report_with_attachment" model="ir.actions.report">
    <field name="name">Report with Attachment</field>
    <field name="model">my.model</field>
    <field name="report_type">qweb-pdf</field>
    <field name="report_name">my_module.my_report</field>
    <field name="attachment_use" eval="True"/>
    <field name="attachment">'my_report_' + str(object.id) + '.pdf'</field>
</record>
```

### Report with Groups

```xml
<record id="report_manager_only" model="ir.actions.report">
    <field name="name">Manager Report</field>
    <field name="model">my.model</field>
    <field name="report_type">qweb-pdf</field>
    <field name="report_name">my_module.manager_report</field>
    <field name="groups_id" eval="[(4, ref('base.group_system'))]"/>
</record>
```

### Print Menu Binding

To show in Print menu:

```xml
<record id="my_report" model="ir.actions.report">
    <field name="name">My Report</field>
    <field name="model">my.model</field>
    <field name="report_type">qweb-pdf</field>
    <field name="report_name">my_module.my_report</field>
    <field name="binding_model_id" ref="model_my_model"/>
    <!-- binding_type automatically 'report' -->
</record>
```

---

## Paper Formats

### report.paperformat Model

Define custom paper sizes and margins.

```xml
<record id="paperformat_euro" model="report.paperformat">
    <field name="name">European A4</field>
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

### Paper Format Fields

| Field | Description | Default |
|-------|-------------|---------|
| `name` | Description/mnemonic | Required |
| `format` | Predefined format or `custom` | A4 |
| `page_height` | Height in mm (if custom) | - |
| `page_width` | Width in mm (if custom) | - |
| `orientation` | `Portrait` or `Landscape` | Portrait |
| `margin_top` | Top margin in mm | - |
| `margin_bottom` | Bottom margin in mm | - |
| `margin_left` | Left margin in mm | - |
| `margin_right` | Right margin in mm | - |
| `header_line` | Show header line | False |
| `header_spacing` | Space before header | - |
| `dpi` | Output DPI | 90 |

### Predefined Formats

A0, A1, A2, A3, A4, A5, A6, A7, A8, A9, A10
B0, B1, B2, B3, B4, B5, B6, B7, B8, B9, B10
Letter, Legal, Tabloid

### Custom Paper Format

```xml
<record id="paperformat_french_check" model="report.paperformat">
    <field name="name">French Bank Check</field>
    <field name="default" eval="True"/>
    <field name="format">custom</field>
    <field name="page_height">80</field>
    <field name="page_width">175</field>
    <field name="orientation">Portrait</field>
    <field name="margin_top">3</field>
    <field name="margin_bottom">3</field>
    <field name="margin_left">3</field>
    <field name="margin_right">3</field>
    <field name="header_line" eval="False"/>
    <field name="header_spacing">3</field>
    <field name="dpi">80</field>
</record>
```

### Using Paper Format

```xml
<report
    id="my_report"
    model="my.model"
    name="my_module.my_report"
    report_type="qweb-pdf"
    paperformat_id="my_module.paperformat_euro"
/>
```

---

## Custom Reports

### Custom Report Model

For additional data in reports, create a custom report model:

```python
from odoo import api, models

class ReportMyModel(models.AbstractModel):
    _name = 'report.my_module.my_report'
    _description = 'Custom My Model Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        # Get the report action
        report = self.env['ir.actions.report']._get_report_from_name(
            'my_module.my_report'
        )

        # Get the records
        docs = self.env[report.model].browse(docids)

        # Custom data
        custom_data = {}
        for doc in docs:
            custom_data[doc.id] = {
                'line_count': len(doc.line_ids),
                'total_amount': sum(line.price_subtotal for line in doc.line_ids),
                'special_field': self._compute_special(doc),
            }

        return {
            'docs': docs,
            'custom_data': custom_data,
        }

    def _compute_special(self, doc):
        # Custom computation
        return "Special Value"
```

### Using Custom Data in Template

```xml
<template id="my_module.my_report">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="o">
            <t t-call="web.external_layout">
                <div class="page">
                    <h2>Document: <span t-field="o.name"/></h2>

                    <!-- Access custom data -->
                    <p>Line Count: <span t-esc="custom_data[o.id]['line_count']"/></p>
                    <p>Total: <span t-esc="custom_data[o.id]['total_amount']"/></p>
                    <p>Special: <span t-esc="custom_data[o.id]['special_field']"/></p>
                </div>
            </t>
        </t>
    </t>
</template>
```

### Custom Report with Related Data

```python
class ReportSaleOrder(models.AbstractModel):
    _name = 'report.sale.order'

    def _get_report_values(self, docids, data=None):
        docs = self.env['sale.order'].browse(docids)

        # Fetch related data
        products = self.env['product.product'].search([
            ('id', 'in', docs.order_line.mapped('product_id').ids)
        ])

        return {
            'docs': docs,
            'products': products,
            'product_categories': self._get_categories(products),
        }

    def _get_categories(self, products):
        categories = products.mapped('categ_id')
        return categories.sorted('name')
```

```xml
<template id="sale.order.report">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="order">
            <t t-call="web.external_layout">
                <div class="page">
                    <h2>Order: <span t-field="order.name"/></h2>

                    <!-- Use custom data -->
                    <h3>Product Categories</h3>
                    <ul>
                        <t t-foreach="product_categories" t-as="cat">
                            <li t-esc="cat.name"/>
                        </t>
                    </ul>
                </div>
            </t>
        </t>
    </t>
</template>
```

---

## Translatable Reports

### Basic Translatable Template

```xml
<!-- Main template -->
<template id="report_saleorder">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="doc">
            <!-- Call translatable template with t-lang -->
            <t t-call="sale.report_saleorder_document" t-lang="doc.partner_id.lang"/>
        </t>
    </t>
</template>

<!-- Translatable template -->
<template id="report_saleorder_document">
    <!-- Re-browse with proper language for translatable fields -->
    <t t-set="doc" t-value="doc.with_context(lang=doc.partner_id.lang)"/>
    <t t-call="web.external_layout">
        <div class="page">
            <p t-field="doc.partner_id.name"/>  <!-- Translated -->
            <p t-field="doc.state"/>  <!-- Translated if selection is translated -->
        </div>
    </t>
</template>
```

### Partial Translation

Translate only the body, keep header/footer in default language:

```xml
<template id="report_saleorder">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="doc">
            <t t-call="web.external_layout" t-lang="en_US">
                <div class="page">
                    <t t-set="doc" t-value="doc.with_context(lang=doc.partner_id.lang)"/>
                    <!-- Content in partner language, header/footer in English -->
                </div>
            </t>
        </t>
    </t>
</template>
```

### Important Notes

- **Only works with `t-call`** - Cannot use `t-lang` on arbitrary XML nodes
- **Re-browse is necessary** - For translatable fields like country names, sales terms
- **Not always needed** - If report doesn't use translatable record fields, skip re-browse (performance)

---

## Barcodes

### Barcode Images

Barcodes are returned by a controller and can be embedded in reports.

```xml
<!-- Basic QR code -->
<img t-att-src="'/report/barcode/QR/%s' % 'My text'"/>

<!-- QR code with query string -->
<img t-att-src="'/report/barcode/?barcode_type=%s&amp;value=%s&amp;width=%s&amp;height=%s' % (
    'QR', 'My text', 200, 200
)"/>

<!-- EAN-13 barcode -->
<img t-att-src="'/report/barcode/?barcode_type=%s&amp;value=%s' % (
    'EAN13', doc.product_id.barcode
)"/>
```

### Barcode Types

| Type | Description |
|------|-------------|
| `QR` | QR Code (2D) |
| `EAN13` | EAN-13 (1D, 13 digits) |
| `EAN8` | EAN-8 (1D, 8 digits) |
| `UPCA` | UPC-A (1D, 12 digits) |
| `Code128` | Code 128 (1D, variable) |
| `Code39` | Code 39 (1D, variable) |
| `ISBN` | ISBN (1D, for books) |

### Barcode Parameters

| Parameter | Description |
|-----------|-------------|
| `barcode_type` | Type of barcode |
| `value` | Data to encode |
| `width` | Width in pixels |
| `height` | Height in pixels |
| `humanreadable` | Show text below barcode (1 or 0) |

### Example: Product Barcode

```xml
<template id="product_report_barcode">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="product">
            <t t-call="web.external_layout">
                <div class="page">
                    <h2 t-field="product.name"/>
                    <p>Barcode: <span t-field="product.barcode"/></p>

                    <!-- Barcode image -->
                    <img t-att-src="'/report/barcode/?barcode_type=%s&amp;value=%s&amp;width=%s&amp;height=%s&amp;humanreadable=1' % (
                        'EAN13',
                        product.barcode or '0000000000000',
                        300,
                        100
                    )"/>
                </div>
            </t>
        </t>
    </t>
</template>
```

---

## Custom Fonts

### Adding Custom Fonts

1. Add font to `web.report_assets_common` bundle
2. Define `@font-face` in CSS
3. Use font in QWeb template

### Step 1: Add Font to Assets

```xml
<template id="report_assets_common_custom_fonts" inherit_id="web.report_assets_common">
    <xpath expr="." position="inside">
        <link href="/my_module/static/src/less/fonts.less" rel="stylesheet" type="text/less"/>
    </xpath>
</template>
```

### Step 2: Define Font Face

```less
/* /my_module/static/src/less/fonts.less */
@font-face {
    font-family: 'MonixBold';
    src: local('MonixBold'),
         local('MonixBold'),
         url(/my_module/static/fonts/MonixBold-Regular.otf) format('opentype');
}

.h1-title-big {
    font-family: MonixBold;
    font-size: 60px;
    color: #3399cc;
}
```

### Step 3: Use in Template

```xml
<template id="my_report">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="doc">
            <t t-call="web.external_layout">
                <div class="page">
                    <h1 class="h1-title-big" t-field="doc.name"/>
                </div>
            </t>
        </t>
    </t>
</template>
```

### Important Notes

- Must add to `web.report_assets_common` (NOT `web.assets_common` or `web.assets_backend`)
- Must define `@font-face` even if defined elsewhere
- Font files go in `static/fonts/` or `static/src/fonts/`

---

## Quick Reference

### Report Declaration

```xml
<report
    id="my_report"
    model="my.model"
    string="My Report"
    report_type="qweb-pdf"
    name="my_module.my_template"
    file="my_report"
    print_report_name="'Report-' + str(object.id)"
    groups_id="base.group_user"
    paperformat_id="my_module.paperformat_custom"
    attachment_use="False"
    binding_model_id="model_my_model"
/>
```

### Template Skeleton

```xml
<template id="my_template">
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

### Common QWeb in Reports

| Directive | Usage |
|-----------|-------|
| `t-call="web.html_container"` | Report wrapper |
| `t-call="web.external_layout"` | Header + footer |
| `div.page` | Main content area |
| `t-field="o.field"` | Smart rendering |
| `t-esc="o.variable"` | Escape + render |
| `t-foreach="docs" t-as="o"` | Loop over records |
| `t-if="condition"` | Condition |
| `t-set="var" t-value="value"` | Set variable |
| `t-attf-href="url"` | Attribute with format |
| `t-lang="lang_code"` | Set translation language |

### Direct URLs

| URL | Description |
|-----|-------------|
| `/report/html/module.report/ID` | HTML version |
| `/report/pdf/module.report/ID` | PDF version |
| `/report/barcode/QR/TEXT` | QR code image |
| `/report/barcode/?barcode_type=...` | Barcode with parameters |

---

**For more Odoo 18 guides, see [SKILL.md](../SKILL.md)**
