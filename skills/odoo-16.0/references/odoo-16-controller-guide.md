---
name: odoo-16-controller
description: Complete reference for Odoo 16 HTTP controllers, routing, authentication types, CSRF, CORS, and request/response handling.
globs: "**/controllers/**/*.py"
topics:
  - Controller basics (class structure, request object)
  - route decorator (URL parameters, route options, multiroute)
  - Authentication types (user, public, none)
  - Request/Response types (http, json)
  - CSRF and CORS handling
  - File uploads and downloads
  - Common patterns (JSON endpoints, file download, website pages, API endpoints, error handling)
when_to_use:
  - Writing HTTP controllers
  - Creating API endpoints
  - Building website pages
  - Handling webhooks and payment callbacks
  - Implementing file uploads/downloads
---

# Odoo 16 Controller Guide

Complete reference for Odoo 16 HTTP controllers, routing, and request handling.

## Table of Contents

1. [Controller Basics](#controller-basics)
2. [@route Decorator](#route-decorator)
3. [Authentication Types](#authentication-types)
4. [Request/Response Types](#requestresponse-types)
5. [Request Object API](#request-object-api)
6. [CSRF Handling](#csrf-handling)
7. [CORS Handling](#cors-handling)
8. [File Uploads](#file-uploads)
9. [File Downloads](#file-downloads)
10. [Common Patterns](#common-patterns)
11. [Best Practices](#best-practices)

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

- Extend `http.Controller`.
- Use `@http.route(...)` decorator on every public method.
- Access `request` (the module-level proxy in `odoo.http`) for env, session, HTTP data.
- Return the right response type for the route `type`.

### Controller Inheritance / Override

In Odoo 16 controllers are extended by Python inheritance (not registry-based). Any method you override MUST be re-decorated with `@http.route()`; arguments you omit are inherited from the parent.

```python
from odoo import http
from odoo.addons.web.controllers.home import Home


class MyHome(Home):

    @http.route()  # keep path, type, auth from parent
    def index(self, *args, **kw):
        # custom logic
        return super().index(*args, **kw)
```

### Module Layout

```
my_module/
├── __init__.py
├── __manifest__.py
├── controllers/
│   ├── __init__.py       # from . import my_module, portal
│   ├── my_module.py
│   └── portal.py          # extends portal controllers
└── ...
```

Remember to `from . import controllers` in the root `__init__.py`.
For new code, name the main controller file after the module. Name a file
that extends another module's controller after that module. `main.py` is a
legacy Odoo convention and may remain in existing addons.

---

## @route Decorator

### Basic Route

```python
from odoo import http


class HelloController(http.Controller):

    @http.route('/hello', type='http', auth='user')
    def hello(self):
        return "Hello World!"
```

### URL Parameters (Werkzeug Converters)

```python
from odoo.http import request

# Integer path parameter
@http.route('/order/<int:order_id>', type='http', auth='user')
def order_view(self, order_id):
    order = request.env['sale.order'].browse(order_id)
    if not order.exists():
        return request.not_found()
    return request.render('sale.order_view', {'order': order})


# Model converter - resolves an ID to a recordset automatically
@http.route('/order/<model("sale.order"):order>', type='http', auth='user')
def order_by_model(self, order):
    return request.render('sale.order_view', {'order': order})


# Wildcard / path parameter
@http.route('/download/<path:file_path>', type='http', auth='user')
def download_any(self, file_path):
    ...


# Query string parameters arrive as kwargs
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
    '/my/path',                 # Route path (or list of paths)
    type='http',                # 'http' or 'json'
    auth='user',                # 'user' (default), 'public', 'none'
    methods=['GET', 'POST'],    # Allowed HTTP methods (None = all)
    csrf=True,                  # CSRF protection (default True for http, False for json)
    cors='*',                   # Access-Control-Allow-Origin value
    website=True,               # Defined by website module; enables website layout/context
    sitemap=False,              # Website-only: include in sitemap
    save_session=True,          # Persist session changes after the request
)
def my_handler(self):
    ...
```

Notes on Odoo 16 specifics:

- `auth` accepts exactly `'user'`, `'public'`, `'none'`. There is NO `auth='bearer'` in v16 (added in later versions). Implement token auth manually with `auth='none'` or `auth='public'` + header check (see API Endpoint pattern below).
- `methods=None` allows every HTTP verb.
- `csrf` default is `True` for `type='http'`, effectively ignored for `type='json'`.
- `website=True` requires the `website` module installed.

### Multiple Paths on One Handler

```python
@http.route(['/path1', '/path2'], type='http', auth='public')
def dual(self):
    return "Same handler for both paths"


# Or stack decorators
@http.route('/alpha', type='http', auth='public')
@http.route('/beta', type='http', auth='public')
def stacked(self):
    return "Hello"
```

---

## Authentication Types

### auth='user' (Default)

Requires an authenticated user. Unauthenticated requests are redirected to the login page.

```python
@http.route('/my/orders', type='http', auth='user')
def my_orders(self):
    orders = request.env['sale.order'].search([
        ('user_id', '=', request.env.user.id),
    ])
    return request.render('my_module.orders', {'orders': orders})
```

Behavior:

- `request.env.user` is the logged-in user.
- `request.env.uid` is that user's id.
- Normal ACL / record rules apply.

### auth='public'

Allows unauthenticated access, using the shared "Public user" record.

```python
@http.route('/shop/products', type='http', auth='public')
def shop_products(self):
    products = request.env['product.product'].search([
        ('website_published', '=', True),
    ])
    return request.render('my_module.shop', {'products': products})
```

Behavior:

- If the visitor is logged in, runs as that user.
- If not, runs as the public user (usually limited access).
- ACL / record rules still apply; use `.sudo()` only when truly needed.

### auth='none'

No environment, no database authentication at all.

```python
@http.route('/healthz', type='http', auth='none', csrf=False)
def healthcheck(self):
    return "OK"
```

Behavior:

- `request.env` is NOT available.
- Route works even when no database is selected.
- Use for static endpoints, health checks, some login screens, or manual token verification against external services.

### Odoo 16 does NOT have `auth='bearer'`

`auth='bearer'` was introduced in later Odoo versions. In 16, implement your own bearer-token logic:

```python
from odoo import http
from odoo.http import request
from werkzeug.exceptions import Unauthorized


class ApiAuth(http.Controller):

    @http.route('/api/v1/me', type='json', auth='none', csrf=False)
    def api_me(self, **params):
        token = request.httprequest.headers.get('Authorization', '')
        if not token.startswith('Bearer '):
            raise Unauthorized()
        token = token[7:]
        # Resolve token -> user (custom model), then manually set up env
        user = request.env(su=True)['api.token']._authenticate(token)
        if not user:
            raise Unauthorized()
        request.update_env(user=user.id)
        return {'login': user.login, 'name': user.name}
```

---

## Request/Response Types

### type='http' - HTML / Text / Binary

The handler's return value can be:

- A `str` or `bytes` (taken as the body).
- An `odoo.http.Response` created with `request.make_response` / `request.render` / `request.redirect` / `request.not_found`.
- A Werkzeug response object.

```python
from odoo.http import request


# Render a QWeb template
@http.route('/page', type='http', auth='user')
def my_page(self):
    return request.render('my_module.template', {
        'records': request.env['my.model'].search([]),
    })


# Plain text
@http.route('/ping', type='http', auth='none')
def ping(self):
    return "PONG"


# Response with headers
@http.route('/inline_pdf/<int:doc_id>', type='http', auth='user')
def inline_pdf(self, doc_id):
    report = request.env.ref('my_module.action_report')
    pdf, _ = report._render_qweb_pdf(report.report_name, [doc_id])
    return request.make_response(pdf, headers=[
        ('Content-Type', 'application/pdf'),
        ('Content-Length', len(pdf)),
    ])


# Redirect (local or absolute)
@http.route('/go', type='http', auth='user')
def go(self):
    return request.redirect('/web')


# 404
@http.route('/maybe/<int:rec_id>', type='http', auth='user')
def maybe(self, rec_id):
    rec = request.env['my.model'].browse(rec_id).exists()
    if not rec:
        return request.not_found()
    return request.render('my_module.detail', {'rec': rec})
```

### type='json' - JSON-RPC 2.0

In Odoo 16, `type='json'` expects a JSON-RPC 2.0 envelope in the POST body:

```json
{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {"id": 42, "limit": 10},
    "id": 1
}
```

The endpoint receives the dict under `"params"` as keyword arguments; the return value is serialized as the `"result"` field of the response.

```python
@http.route('/api/records', type='json', auth='user')
def get_records(self, domain=None, limit=80, offset=0):
    domain = domain or []
    records = request.env['my.model'].search_read(
        domain, ['id', 'name', 'state'],
        limit=limit, offset=offset,
    )
    return {'records': records, 'count': len(records)}
```

Calling from OWL:

```javascript
// Using the rpc service (Odoo 16 pattern)
this.rpc = useService("rpc");
const res = await this.rpc("/api/records", { domain: [["state", "=", "open"]], limit: 20 });
```

`type='json'` behavior:

- CSRF is disabled by default (the JSON-RPC client handles the exchange).
- Exceptions raised in the handler are serialized as JSON-RPC errors.
- Python `UserError` / `AccessError` surface to the browser as user-friendly dialogs.

---

## Request Object API

`from odoo.http import request`

### Environment

```python
request.env            # odoo.api.Environment bound to the authenticated user
request.env.user       # res.users recordset (the current user)
request.env.company    # Current company (res.company)
request.env.companies  # Allowed companies (res.company recordset)
request.env.lang       # Language code of the user's context
request.env.uid        # Integer user id
request.env.context    # Context dict (lang, tz, allowed_company_ids, ...)
```

You can `.sudo()` the env like in any ORM context:

```python
partner = request.env['res.partner'].sudo().browse(partner_id)
```

### Session

```python
request.session              # dict-like Session object
request.session.uid          # Logged-in user id (or None)
request.session.db           # Current database name
request.session['cart_id']   # Custom session entries (must be JSON-serialisable)
request.session.get('foo')   # Safe read
```

### HTTP Data

```python
request.httprequest            # Underlying werkzeug.wrappers.Request
request.httprequest.method     # 'GET', 'POST', ...
request.httprequest.headers    # werkzeug Headers
request.httprequest.files      # FileStorage dict (multipart uploads)
request.httprequest.remote_addr
request.params                 # Merged query string + form body + JSON params
request.db                     # Current db name or None
request.csrf_token()           # Fresh CSRF token (use in forms)
```

### Response Helpers

```python
request.render(template, values=None, **kw)       # Lazy QWeb rendering
request.make_response(body, headers=None, cookies=None, status=200)
request.make_json_response(data, headers=None, cookies=None, status=200)
request.not_found(description=None)
request.redirect(location, code=303, local=True)
request.redirect_query(location, query=None, code=303, local=True)
```

---

## CSRF Handling

### Default Behavior

- `type='http'` POST/PUT/DELETE require a CSRF token (`csrf_token` form field).
- GET/HEAD/OPTIONS never require CSRF.
- `type='json'` doesn't check CSRF (JSON-RPC clients handle the exchange themselves).

### Form with CSRF Token

```xml
<form action="/my/form/submit" method="POST">
    <input type="hidden" name="csrf_token" t-att-value="request.csrf_token()"/>
    <input type="text" name="email"/>
    <button type="submit">Send</button>
</form>
```

```python
@http.route('/my/form/submit', type='http', auth='public', methods=['POST'])
def form_submit(self, email=None, **kw):
    # csrf_token already validated by the framework
    request.env['newsletter.signup'].sudo().create({'email': email})
    return request.redirect('/thanks')
```

### Disabling CSRF (Webhooks / Server-to-Server)

Only disable CSRF for endpoints you protect another way (HMAC signature, IP whitelist, bearer token):

```python
@http.route('/webhook/payment', type='http', auth='none', methods=['POST'], csrf=False)
def payment_webhook(self, **kwargs):
    signature = request.httprequest.headers.get('X-Hub-Signature')
    # Verify HMAC here
    ...
    return "OK"
```

---

## CORS Handling

Set the `cors` option on the route. Odoo 16 emits `Access-Control-Allow-Origin` and automatically serves preflight OPTIONS with compatible headers.

```python
@http.route('/api/v1/status', type='json', auth='none', cors='*', csrf=False)
def api_status(self):
    return {'status': 'ok'}


# Restrict to a specific origin
@http.route('/api/v1/orders', type='json', auth='user', cors='https://partner.example.com')
def api_orders(self, **kw):
    ...
```

For public APIs, combine `cors='*'` with `csrf=False` (since browsers can't send CSRF tokens cross-origin). Prefer `type='json'` so the framework handles preflight correctly.

---

## File Uploads

Multipart file uploads arrive in `request.httprequest.files`. Each entry is a `werkzeug.datastructures.FileStorage`.

```python
import base64

from odoo import http
from odoo.http import request


class UploadController(http.Controller):

    @http.route('/my/upload', type='http', auth='user', methods=['POST'])
    def upload(self, **post):
        upload = request.httprequest.files.get('file')
        if not upload:
            return request.make_response("No file", status=400)

        data = upload.read()  # bytes
        attachment = request.env['ir.attachment'].create({
            'name': upload.filename,
            'datas': base64.b64encode(data),
            'mimetype': upload.mimetype,
            'res_model': 'my.model',
            'res_id': int(post.get('res_id', 0)) or False,
        })
        return request.redirect(f'/web#id={attachment.res_id}&model=my.model')
```

HTML form:

```xml
<form action="/my/upload" method="POST" enctype="multipart/form-data">
    <input type="hidden" name="csrf_token" t-att-value="request.csrf_token()"/>
    <input type="hidden" name="res_id" t-att-value="rec.id"/>
    <input type="file" name="file"/>
    <button type="submit">Upload</button>
</form>
```

For large uploads, stream with `upload.stream` instead of `upload.read()`.

---

## File Downloads

### Option 1: `request.make_response` (small payloads)

```python
@http.route('/download/report/<int:report_id>', type='http', auth='user')
def download_report(self, report_id):
    report = request.env['ir.actions.report'].browse(report_id)
    pdf, _ = report._render_qweb_pdf(report.report_name, [report_id])
    return request.make_response(pdf, headers=[
        ('Content-Type', 'application/pdf'),
        ('Content-Disposition', f'attachment; filename="{report.name}.pdf"'),
        ('Content-Length', len(pdf)),
    ])
```

### Option 2: `http.Stream` (Odoo 16 preferred helper)

`odoo.http.Stream` is the recommended way to serve files or binary fields with proper caching, ETag, and conditional support.

```python
from odoo import http
from odoo.http import Stream, request


class DownloadController(http.Controller):

    @http.route('/download/attachment/<int:attachment_id>', type='http', auth='user')
    def download_attachment(self, attachment_id):
        attachment = request.env['ir.attachment'].browse(attachment_id).exists()
        if not attachment:
            return request.not_found()
        attachment.check('read')  # ACL
        return Stream.from_attachment(attachment).get_response(as_attachment=True)

    @http.route('/download/field/<int:rec_id>', type='http', auth='user')
    def download_binary_field(self, rec_id):
        rec = request.env['my.model'].browse(rec_id).exists()
        if not rec:
            return request.not_found()
        return Stream.from_binary_field(rec, 'binary_field').get_response(
            as_attachment=True,
        )
```

`Stream` constructors in v16:

- `Stream.from_path(path, filter_ext=('',), public=False)` — serve a file on disk.
- `Stream.from_attachment(attachment)` — from an `ir.attachment` record.
- `Stream.from_binary_field(record, field_name)` — from a binary/image field.

---

## Common Patterns

### JSON Endpoint for Frontend

```python
from odoo import http
from odoo.http import request


class MyWebController(http.Controller):

    @http.route('/my/data', type='json', auth='user')
    def get_data(self, domain=None, fields=None):
        domain = domain or []
        fields = fields or ['id', 'name', 'date']
        records = request.env['my.model'].search_read(domain, fields)
        return {'records': records, 'count': len(records)}

    @http.route('/my/action', type='json', auth='user')
    def do_action(self, record_id, action_type):
        record = request.env['my.model'].browse(record_id).exists()
        if not record:
            return {'error': 'Record not found'}
        if action_type == 'validate':
            record.action_validate()
        elif action_type == 'cancel':
            record.action_cancel()
        return {'success': True, 'state': record.state}
```

OWL side:

```javascript
/** @odoo-module **/
import { useService } from "@web/core/utils/hooks";

setup() {
    this.rpc = useService("rpc");
}

async loadData() {
    const res = await this.rpc("/my/data", { domain: [["state", "=", "open"]] });
    this.state.records = res.records;
}
```

### Website Page

```python
from odoo import http
from odoo.http import request


class WebsiteCatalog(http.Controller):

    @http.route('/shop', type='http', auth='public', website=True, sitemap=True)
    def shop(self, **kw):
        products = request.env['product.template'].search([
            ('website_published', '=', True),
            ('sale_ok', '=', True),
        ])
        return request.render('my_module.shop', {
            'products': products,
        })

    @http.route('/shop/<model("product.template"):product>',
                type='http', auth='public', website=True)
    def product(self, product, **kw):
        return request.render('my_module.product', {
            'product': product,
        })
```

### External API Endpoint (Token-Protected)

```python
from odoo import http
from odoo.http import request
from werkzeug.exceptions import Forbidden


class SalesApi(http.Controller):

    def _check_api_key(self):
        key = request.httprequest.headers.get('X-Api-Key')
        expected = request.env['ir.config_parameter'].sudo().get_param('my_module.api_key')
        if not key or key != expected:
            raise Forbidden()

    @http.route('/api/v1/orders', type='json', auth='user', csrf=False, cors='*')
    def list_orders(self, domain=None, limit=80):
        self._check_api_key()
        orders = request.env['sale.order'].sudo().search_read(
            domain or [],
            ['id', 'name', 'state', 'amount_total', 'partner_id'],
            limit=limit,
        )
        return {'orders': orders}

    @http.route('/api/v1/orders/<int:order_id>', type='json', auth='user', csrf=False, cors='*')
    def get_order(self, order_id):
        self._check_api_key()
        order = request.env['sale.order'].sudo().browse(order_id).exists()
        if not order:
            return {'error': 'not_found'}
        return order.read(['name', 'state', 'amount_total'])[0]
```

### Webhook (No CSRF, HMAC-Verified)

```python
import hmac
import hashlib

from odoo import http
from odoo.http import request


class StripeWebhook(http.Controller):

    @http.route('/webhook/stripe', type='http', auth='none',
                methods=['POST'], csrf=False)
    def stripe_webhook(self, **kwargs):
        secret = request.env(su=True)['ir.config_parameter'].get_param('stripe.webhook_secret')
        signature = request.httprequest.headers.get('Stripe-Signature', '')
        payload = request.httprequest.get_data()
        expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, signature):
            return request.make_response("bad signature", status=400)
        # Process event
        ...
        return "OK"
```

### Error Handling

```python
from odoo import http
from odoo.http import request
from odoo.exceptions import UserError, AccessError


class ActionController(http.Controller):

    @http.route('/action', type='json', auth='user')
    def do_action(self, record_id):
        try:
            record = request.env['my.model'].browse(record_id)
            record.action_validate()
            return {'success': True}
        except AccessError as e:
            return {'error': 'access_denied', 'message': str(e)}
        except UserError as e:
            return {'error': 'user_error', 'message': str(e)}

    @http.route('/page', type='http', auth='user')
    def my_page(self):
        try:
            return request.render('my_module.template', {
                'data': self._get_data(),
            })
        except UserError as e:
            return request.render('my_module.error', {'message': str(e)})
        except Exception:
            return request.not_found()
```

### Response Methods Quick Reference

```python
request.render('module.template', values)                     # Lazy QWeb render
request.make_response(body, headers=[...], status=200)        # Raw body + headers
request.make_json_response({'key': 'value'}, status=200)      # JSON body
request.redirect('/somewhere')                                # 303 redirect (local)
request.redirect('https://other.example', local=False)        # Absolute redirect
request.not_found()                                           # 404
```

---

## Best Practices

1. **Keep controllers thin.** Move business logic into models. Controllers handle HTTP concerns only.
2. **Pick the right `type`.** `'http'` for pages, forms, downloads; `'json'` for frontend RPC calls and machine APIs.
3. **Default to `auth='user'`.** Use `'public'` only for unauthenticated features; `'none'` only when you must bypass the ORM entirely.
4. **Don't `sudo()` by reflex.** Prefer proper ACLs / record rules; `sudo()` is for deliberate privilege elevation.
5. **Validate inputs.** `int(kwargs.get('id', 0))`, enum whitelists, length checks — the browser is untrusted.
6. **Check existence.** `rec.exists()` before operating on browsed ids.
7. **Respect CSRF.** Only disable it when you authenticate the request another way (HMAC, API key, bearer token).
8. **Set `cors` explicitly for JSON APIs** used cross-origin, and pair with `csrf=False`.
9. **Use `Stream` for downloads.** Proper caching, ETag, conditional GET come for free.
10. **Raise werkzeug exceptions for HTTP errors** (`NotFound`, `Forbidden`, `BadRequest`) rather than returning ad-hoc strings.

---

## Base Code Reference

The APIs documented here are defined in the Odoo 16 source:

- `odoo/http.py` — `Controller`, `route`, `Request`, `Response`, `Stream`, session, dispatching.
- `odoo/exceptions.py` — `UserError`, `AccessError`, `ValidationError`.
- `addons/web/controllers/report.py` — reference controllers, e.g. `/report/barcode`, `/report/download`.
- `addons/web/controllers/home.py` — base web client routes (useful for inheritance examples).
