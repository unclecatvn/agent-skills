# Odoo 18 Controller Guide

Complete reference for Odoo 18 HTTP controllers, routing, and request handling.

## Table of Contents

1. [Controller Basics](#controller-basics)
2. [@route Decorator](#route-decorator)
3. [Authentication Types](#authentication-types)
4. [Request/Response Types](#requestresponse-types)
5. [CSRF Handling](#csrf-handling)
6. [Common Patterns](#common-patterns)

---

## Controller Basics

### Controller Class Structure

```python
from odoo import http
from odoo.http import request

class MyController(http.Controller):

    @http.route('/my/path', type='http', auth='user')
    def my_handler(self, **kwargs):
        return request.render('my_module.template', {
            'records': request.env['my.model'].search([]),
        })
```

**Key points**:
- Extend `http.Controller`
- Use `@http.route()` decorator
- Access `request` for environment and data
- Return appropriate response type

### Request Object

```python
# Environment access (same as model.env)
request.env  # Current environment
request.env.user  # Current user
request.env.company  # Current company
request.env.lang  # Current language

# Session access
request.session  # Current session dict
request.session['key'] = 'value'  # Set session value
request.session.get('key')  # Get session value

# HTTP data
request.httprequest  # Werkzeug request object
request.params  # URL parameters
request.csrf_token()  # Current CSRF token

# Database
request.db  # Current database name
request.cr  # Database cursor (rarely needed)
```

---

## @route Decorator

### Basic Route

```python
from odoo import http

@http.route('/hello', type='http', auth='user')
def hello(self):
    return "Hello World!"
```

### URL Parameters

```python
# Path parameter
@http.route('/order/<int:order_id>', type='http', auth='user')
def order_view(self, order_id):
    order = request.env['sale.order'].browse(order_id)
    if not order.exists():
        return request.not_found()
    return request.render('sale.order_view', {'order': order})

# Query parameters
@http.route('/search', type='http', auth='user')
def search_orders(self, **kwargs):
    domain = []
    if kwargs.get('name'):
        domain.append(('name', 'ilike', kwargs['name']))
    orders = request.env['sale.order'].search(domain)
    return request.render('sale.order_list', {'orders': orders})
```

### Route Options

```python
@http.route(
    '/my/path',                    # Route path
    type='http',                   # 'http' or 'json'
    auth='user',                   # 'public', 'user', 'none'
    methods=['GET', 'POST'],       # Allowed HTTP methods
    csrf=True,                     # CSRF validation
    website=True,                  # Website route (render with website layout)
    sitemap=False,                 # Include in sitemap
    save_session=True,             # Save session after request
)
def my_handler(self):
    pass
```

### Multiroute (Same Handler, Multiple Paths)

```python
@http.route('/path1')
@http.route('/path2')
def my_handler(self):
    return "Same handler for both paths"
```

---

## Authentication Types

### auth='user' (Default)

**Requires**: Logged-in user

```python
@http.route('/my/orders', type='http', auth='user')
def my_orders(self):
    # request.env.user is available
    orders = request.env['sale.order'].search([
        ('user_id', '=', request.env.user.id)
    ])
    return request.render('my_orders', {'orders': orders})
```

**Behavior**:
- Redirects to login if not authenticated
- `request.env.uid` is the logged-in user
- Normal record access rules apply

### auth='public'

**Allows**: Access without login (with access rights)

```python
@http.route('/shop/products', type='http', auth='public')
def shop_products(self):
    # Public can access, but respects access rights
    products = request.env['product.product'].search([
        ('website_published', '=', True)
    ])
    return request.render('shop_products', {'products': products})
```

**Behavior**:
- No redirect to login
- `request.env.uid` is anonymous (usually 3-4)
- Access rights still enforced (public user has limited access)
- Use `sudo()` to bypass access rights if needed

### auth='none'

**Allows**: No environment, no access rights

```python
@http.route('/web/webclient/locale', type='http', auth='none')
def get_locale(self):
    # No environment available - no request.env
    # Return static data
    return request.make_json_response({
        'lang': 'en_US',
        'direction': 'ltr',
    })
```

**Behavior**:
- `request.env` is NOT available
- No database access
- For truly public, static endpoints
- Used for login pages, health checks

---

## Request/Response Types

### type='http' - HTML/Text Response

```python
from odoo.http import request

# Render QWeb template
@http.route('/page', type='http', auth='user')
def my_page(self):
    return request.render('my_module.template', {
        'records': request.env['my.model'].search([]),
    })

# Return plain text
@http.route('/ping', type='http', auth='none')
def ping(self):
    return "PONG"

# Return HTML directly
@http.route('/html', type='http', auth='user')
def html_response(self):
    return "<h1>Hello</h1>"

# Make response with headers
@http.route('/download', type='http', auth='user')
def download_file(self):
    return request.make_response(
        data,
        headers=[
            ('Content-Type', 'application/pdf'),
            ('Content-Disposition', 'attachment; filename="file.pdf"'),
        ]
    )

# Redirect
@http.route('/redirect', type='http', auth='user')
def redirect_example(self):
    return request.redirect('/target/url')
```

### type='json' - JSON-RPC Response

```python
@http.route('/api/action', type='json', auth='user')
def json_action(self, **kwargs):
    # For JSON-RPC, return data directly (converted to JSON)
    record = request.env['my.model'].browse(kwargs.get('id'))
    return {
        'status': 'success',
        'data': {
            'name': record.name,
            'value': record.value,
        }
    }

# JSON endpoints are called from frontend
// Frontend call
this.rpc('/api/action', {id: 123}).then(result => {
    console.log(result);
});
```

**type='json' behavior**:
- Automatically serializes return value to JSON
- Used for frontend JavaScript calls
- CSRF token handled automatically from frontend

---

## CSRF Handling

### CSRF Protection (Default)

```python
# CSRF enabled by default for POST
@http.route('/form/submit', type='http', auth='user', methods=['POST'])
def form_submit(self, **kwargs):
    # CSRF token validated automatically
    # Process form data...
    return "Form submitted"
```

### Disable CSRF (Use Carefully)

```python
# For external webhooks, payment callbacks
@http.route('/webhook/payment', type='http', auth='none', csrf=False)
def payment_webhook(self):
    # Verify request another way (signature, IP whitelist)
    # Process webhook...
    return "OK"
```

### CSRF Token in Forms

```xml
<!-- QWeb template with CSRF token -->
<form t-action="/form/submit" method="POST">
    <input type="hidden" name="csrf_token" t-att-value="request.csrf_token()"/>
    <!-- other fields -->
</form>
```

---

## Common Patterns

### JSON Endpoint for Frontend

```python
from odoo import http
from odoo.http import request

class MyController(http.Controller):

    @http.route('/my/data', type='json', auth='user')
    def get_data(self, domain=None, fields=None):
        """JSON endpoint for frontend widgets"""
        domain = domain or []
        fields = fields or ['id', 'name', 'date']

        records = request.env['my.model'].search_read(domain, fields)
        return {
            'records': records,
            'count': len(records),
        }

    @http.route('/my/action', type='json', auth='user')
    def do_action(self, record_id, action_type):
        """Handle action from frontend"""
        record = request.env['my.model'].browse(record_id)
        if not record.exists():
            return {'error': 'Record not found'}

        if action_type == 'validate':
            record.action_validate()
        elif action_type == 'cancel':
            record.action_cancel()

        return {'success': True, 'status': record.state}
```

### File Download

```python
from odoo import http
from odoo.http import request

class DownloadController(http.Controller):

    @http.route('/download/report/<int:report_id>', type='http', auth='user')
    def download_report(self, report_id):
        """Download generated report"""
        report = request.env['ir.actions.report'].browse(report_id)

        # Get the report content
        pdf_content, _ = report._render_qweb_pdf([report_id])

        return request.make_response(
            pdf_content,
            headers=[
                ('Content-Type', 'application/pdf'),
                ('Content-Disposition', f'attachment; filename="{report.name}.pdf"'),
            ]
        )

    @http.route('/download/attachment/<int:attachment_id>', type='http', auth='user')
    def download_attachment(self, attachment_id):
        """Download attachment"""
        attachment = request.env['ir.attachment'].browse(attachment_id)
        if not attachment.exists():
            return request.not_found()

        return request.make_response(
            attachment.datas,
            headers=[
                ('Content-Type', attachment.mimetype),
                ('Content-Disposition', f'attachment; filename="{attachment.name}"'),
            ]
        )
```

### Website Page

```python
from odoo import http
from odoo.http import request

class WebsiteController(http.Controller):

    @http.route('/shop', type='http', auth='public', website=True)
    def shop(self, **kwargs):
        """Website shop page"""
        products = request.env['product.product'].search([
            ('website_published', '=', True),
            ('sale_ok', '=', True),
        ])

        # Get cart
        cart = request.website.sale_get_order()

        return request.render('website_shop.shop', {
            'products': products,
            'cart': cart,
        })

    @http.route('/shop/product/<model("product.product"):product>', type='http', auth='public', website=True)
    def product(self, product, **kwargs):
        """Product detail page"""
        return request.render('website_shop.product', {
            'product': product,
            'related_products': product.product_tmpl_id.product_variant_ids,
        })
```

### API Endpoint (External Integration)

```python
from odoo import http
from odoo.http import request

class ApiController(http.Controller):

    @http.route('/api/v1/orders', type='json', auth='user', csrf=False)
    def api_orders(self, domain=None, limit=80):
        """External API endpoint"""
        # Use sudo() to ensure access, or validate access manually
        orders = request.env['sale.order'].sudo().search(
            domain or [],
            limit=limit
        )
        return orders.read(['name', 'state', 'amount_total'])

    @http.route('/api/v1/order/<int:order_id>', type='json', auth='user', methods=['GET'])
    def api_order_get(self, order_id):
        """Get single order"""
        order = request.env['sale.order'].sudo().browse(order_id)
        if not order.exists():
            return request.make_json_response(
                {'error': 'Order not found'},
                status=404
            )
        return order.read([])[0]
```

### Error Handling

```python
from odoo import http
from odoo.http import request
from odoo.exceptions import UserError, AccessError

class MyController(http.Controller):

    @http.route('/action', type='json', auth='user')
    def do_action(self, record_id):
        try:
            record = request.env['my.model'].browse(record_id)
            record.action_validate()
            return {'success': True}
        except AccessError:
            return {
                'error': 'Access denied',
                'error_type': 'access_error'
            }
        except UserError as e:
            return {
                'error': str(e),
                'error_type': 'user_error'
            }
        except Exception as e:
            return {
                'error': 'An error occurred',
                'error_type': 'system_error'
            }

    @http.route('/page', type='http', auth='user')
    def my_page(self):
        try:
            data = self._get_data()
            return request.render('template', {'data': data})
        except Exception:
            return request.redirect('/error')
```

### Response Methods Reference

```python
# Render template with website layout
request.render('module.template', values)

# Render with custom response
request.make_response(html, headers=[...])

# JSON response
request.make_json_response({'key': 'value'})

# Redirect
request.redirect('/target/url')

# 404 Not Found
request.not_found()

# HTTP error
request.make_json_response({'error': 'message'}, status=400)
```

---

## Controller Best Practices

1. **Keep controllers thin** - Move business logic to models
2. **Use appropriate auth** - Don't use `sudo()` unless necessary
3. **Validate input** - Check parameters before database operations
4. **Handle exceptions** - Return meaningful error messages
5. **Use correct type** - `json` for frontend, `http` for pages
6. **Respect CSRF** - Only disable for external APIs
6. **Return proper responses** - Use correct response methods
