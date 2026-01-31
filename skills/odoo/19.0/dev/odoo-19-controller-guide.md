# Odoo 19 Controller Guide

Guide for creating HTTP controllers and routes in Odoo 19.

## Table of Contents
- [Controllers](#controllers)
- [Routes](#routes)
- [Request](#request)
- [Response](#response)
- [Authentication](#authentication)
- [JSON-RPC](#json-rpc)

---

## Controllers

Controllers provide extensibility similar to models, but with a separate mechanism (since database may not be available).

Controllers are created by inheriting from `odoo.http.Controller`:

```python
from odoo import http

class MyController(http.Controller):
    @http.route('/some_url', auth='public')
    def handler(self):
        return stuff()
```

### Controller Inheritance

To override a controller, inherit from its class and override methods:

```python
class Extension(MyController):
    @http.route()
    def handler(self):
        do_before()
        return super(Extension, self).handler()
```

**Important**:
- Always re-apply `@http.route()` decorator to keep route visible
- Without decorator, method is "unpublished"
- Decorator arguments override previous ones

### Change Authentication

```python
class Restrict(MyController):
    @http.route(auth='user')
    def handler(self):
        return super(Restrict, self).handler()
```

This changes `/some_url` from public to user (requires login).

---

## Routes

### Route Decorator

`@http.route()` defines routing for controller methods.

```python
@http.route('/hello', auth='public', website=True)
def hello(self):
    return "Hello World!"
```

### Route Parameters

| Parameter | Description |
|-----------|-------------|
| `route` | Route path(s) (string or list) |
| `auth` | Authentication type (`public`, `user`, `none`) |
| `methods` | Allowed HTTP methods (`GET`, `POST`, etc.) |
| `type` | Response type (`http`, `json`) |
| `website` | Boolean: bind to current website |
| `csrf` | Boolean: CSRF protection (default: True) |
| `sitemap` | Boolean or sitemap config |

### Multiple Routes

```python
@http.route(['/hello', '/bonjour'], auth='public')
def hello_bonjour(self):
    return "Hello or Bonjour!"
```

### HTTP Methods

```python
@http.route('/api/data', methods=['GET'], auth='user', type='json')
def get_data(self):
    return {'data': 'value'}

@http.route('/api/data', methods=['POST'], auth='user', type='json')
def post_data(self, **kwargs):
    return {'result': 'created'}
```

---

## Authentication

### Authentication Types

| Type | Description |
|------|-------------|
| `public` | No authentication required |
| `user` | Requires active user session |
| `none` | No authentication, no session |
| `website` | Public with website support |

### Examples

```python
# Public route
@http.route('/page', auth='public')
def public_page(self):
    return "Everyone can see this"

# User-only route
@http.route('/my-account', auth='user')
def user_page(self):
    return "Only logged users can see this"

# No authentication
@http.route('/api/status', auth='none', type='json')
def status(self):
    return {'status': 'ok'}
```

### Current User

```python
@http.route('/profile', auth='user')
def profile(self):
    # Access current user
    user = http.request.env.user
    return f"Hello, {user.name}"
```

---

## Request

The request object is automatically set on `odoo.http.request` at the start of each request.

### Request Properties

| Property | Description |
|----------|-------------|
| `httprequest` | Original Werkzeug request |
| `env` | Odoo environment for current request |
| `db` | Current database |
| `uid` | Current user id |
| `context` | Request context |
| `session` | Session |
| `cr` | Database cursor |
| `lang` | Current language |
| `registry` | Model registry |

### Example

```python
@http.route('/info', auth='user')
def info(self):
    request = http.request
    user = request.env.user
    company = request.env.company
    return f"{user.name} @ {company.name}"
```

### Session

```python
@http.route('/set-value', auth='public', methods=['POST'])
def set_value(self, key, value):
    http.request.session[key] = value
    return "OK"

@http.route('/get-value', auth='public')
def get_value(self, key):
    return http.request.session.get(key, 'not set')
```

---

## Response

### HTTP Response

Return string for HTML, dict for JSON:

```python
# HTML response
@http.route('/html', auth='public', type='http')
def html_response(self):
    return "<h1>Hello</h1>"

# JSON response
@http.route('/json', auth='public', type='json')
def json_response(self):
    return {'key': 'value'}
```

### Redirect

```python
from odoo.http import redirect

@http.route('/old-url', auth='public')
def old_url(self):
    return redirect('/new-url')
```

### File Response

```python
@http.route('/download', auth='user')
def download_file(self):
    file_content = b'file data'
    headers = [
        ('Content-Type', 'application/pdf'),
        ('Content-Disposition', 'attachment; filename="file.pdf"'),
    ]
    return request.make_response(
        file_content,
        headers
    )
```

---

## JSON-RPC

### JSON Controller

```python
@http.route('/api/search', auth='user', type='json', methods=['POST'])
def json_search(self, model, domain, fields=None):
    Model = http.request.env[model]
    records = Model.search(domain)
    if fields:
        records = records.read(fields)
    else:
        records = records.read()
    return {'result': records}
```

### Call from JavaScript

```javascript
rpc('/api/search', {
    model: 'res.partner',
    domain: [['is_company', '=', true]],
    fields: ['name', 'email']
}).then(function(result) {
    console.log(result);
});
```

---

## Website Routes

### Website Page

```python
class WebsiteController(http.Controller):
    @http.route('/my-page', auth='public', website=True)
    def my_page(self):
        return http.request.render('my_module.my_page_template', {
            'title': 'My Page',
        })
```

### Template

```xml
<template id="my_page_template" name="My Page">
    <t t-call="website.layout">
        <div id="wrap">
            <div class="oe_structure"/>
            <h1 t-esc="title"/>
            <div class="oe_structure"/>
        </div>
    </t>
</template>
```

---

## Controllers Best Practices

### Always Return a Value

```python
# BAD: no return
@http.route('/bad', auth='public')
def bad(self):
    pass

# GOOD: return something
@http.route('/good', auth='public')
def good(self):
    return "Response"
```

### Use Proper Authentication

```python
# BAD: public for sensitive data
@http.route('/sensitive', auth='public')
def sensitive(self):
    return secret_data()

# GOOD: user authentication
@http.route('/sensitive', auth='user')
def sensitive(self):
    return secret_data()
```

### CSRF Protection

CSRF is enabled by default for POST. Disable with caution:

```python
@http.route('/webhook', auth='public', methods=['POST'], csrf=False)
def webhook(self):
    # External webhook, no CSRF token
    return "OK"
```

---

## References

- Source: Odoo 19 documentation `/doc/developer/reference/backend/http.rst`
