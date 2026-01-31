# Tài liệu Phát triển Odoo (Odoo Development Guides)

![npm](https://img.shields.io/badge/npm-%40unclecat--agent--skills--cli-blue?style=flat-square&logo=npm&label=CLI)
![Node](https://img.shields.io/badge/node-%3E%3D18.0.0-green?style=flat-square&logo=node.js)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)

Bộ tài liệu hướng dẫn phát triển Odoo toàn diện cho nhiều phiên bản, được tối ưu hóa cho AI Assistants (Cursor, Claude Code, Antigravity, v.v.).

## 📚 Các phiên bản hỗ trợ

Hiện tại chúng tôi cung cấp tài liệu chi tiết cho các phiên bản sau:

- **[Odoo 19.0 (Mới nhất)](./19.0/)**: Bao gồm 21+ hướng dẫn (OWL, ORM, Mixins, Testing, v.v.)
- **[Odoo 18.0](./18.0/)**: Bao gồm 18+ hướng dẫn tập trung vào ORM và Web Client mới.

## Giới thiệu

## Đây là hệ sinh thái tài liệu tham khảo hoàn chỉnh cho phát triển Odoo, được tổ chức thành các module nhỏ giúp AI dễ dàng tiêu thụ và cung cấp ngữ cảnh chính xác. Tài liệu được cập nhật liên tục dựa trên mã nguồn Odoo gốc.

## Hướng dẫn các phiên bản

Mỗi phiên bản Odoo có cấu trúc tài liệu tương tự nhau nhưng nội dung được điều chỉnh theo đặc thù version:

- **[Tài liệu Odoo 19.0](./19.0/SKILL.md)**: Đầy đủ nhất, bao gồm OWL Framework, Testing, Migration.
- **[Tài liệu Odoo 18.0](./18.0/SKILL.md)**: Tập trung vào ORM, View, Performance.

#### Cấu trúc tiêu biểu (Odoo 19):

```
skills/odoo/19.0/
├── SKILL.md                       # Index chính
├── dev/
│   ├── odoo-19-owl-guide.md       # OWL Framework (Mới)
│   ├── odoo-19-model-guide.md     # ORM/CRUD
│   ├── odoo-19-view-guide.md      # XML Views (list, form)
│   ├── odoo-19-testing-guide.md   # Testing (Mới)
│   └── ... (21+ files)
```

## Các hướng dẫn

### 1. Development Guide (`odoo-18-development-guide.md`)

Hướng dẫn tạo module Odoo 18 hoàn chỉnh:

- Cấu trúc thư mục module
- `__manifest__.py` và tất cả các trường
- Bảo mật: Access Rights, Record Rules, Groups
- Báo cáo QWeb-PDF, QWeb-HTML
- Wizard và TransientModel
- Cron jobs, Server Actions
- Hooks (post_init, pre_init, uninstall)

### 2. Model Guide (`odoo-18-model-guide.md`)

Tham khảo ORM và thao tác dữ liệu:

- Recordset basics: `browse()`, `exists()`
- Search methods: `search()`, `search_read()`, `read_group()`
- CRUD operations: `create()`, `read()`, `write()`, `unlink()`
- Domain syntax và operators
- Environment context: `with_context()`, `with_user()`, `with_company()`

### 3. Field Guide (`odoo-18-field-guide.md`)

Tất cả các loại field trong Odoo 18:

- Simple fields: `Char`, `Text`, `Html`, `Boolean`, `Integer`, `Float`, `Monetary`, `Date`, `Datetime`, `Binary`, `Selection`
- Relational fields: `Many2one`, `One2many`, `Many2many`
- Computed fields với `compute`, `store`, `search`, `inverse`
- Related fields
- Field parameters: `index`, `default`, `copy`, `groups`, `company_dependent`

### 4. Decorator Guide (`odoo-18-decorator-guide.md`)

API Decorators của Odoo:

- `@api.model` - Model-level methods
- `@api.depends` - Computed fields (hỗ trợ dotted paths)
- `@api.depends_context` - Context-dependent computed fields
- `@api.constrains` - Validation (KHÔNG hỗ trợ dotted paths)
- `@api.onchange` - Form UI updates
- `@api.ondelete` - Delete validation (Odoo 18 mới)
- `@api.returns` - Return type specification

### 5. View Guide (`odoo-18-view-guide.md`)

XML Views và QWeb templates:

- View types: `list` (đổi từ `tree`), `form`, `search`, `kanban`, `graph`, `pivot`, `calendar`
- List view features: `editable`, `decoration`, `optional`, widgets
- Form view structure: sheet, button box, notebook, chatter
- Search view: filters, group by
- Actions: window, server, client, report
- Menus
- View inheritance với XPath

### 6. Performance Guide (`odoo-18-performance-guide.md`)

Tối ưu hiệu năng Odoo:

- Prefetch mechanism (PREFETCH_MAX = 1000)
- Ngăn chặn N+1 queries
- Batch operations (create, write, unlink)
- Field selection optimization
- Compute field optimization
- SQL optimization với `execute_query_dict()`

### 7. Controller Guide (`odoo-18-controller-guide.md`)

HTTP controllers và routing:

- Controller class structure
- `@route` decorator với URL parameters
- Authentication types: `auth='user'`, `auth='public'`, `auth='none'`
- Request/Response types: `type='http'`, `type='json'`
- CSRF handling
- Common patterns: JSON endpoints, file download, website pages

## Các thay đổi chính trong Odoo 18

| Thay đổi          | Odoo 17             | Odoo 18                             |
| ----------------- | ------------------- | ----------------------------------- |
| List view tag     | `<tree>`            | `<list>`                            |
| Delete validation | Override `unlink()` | `@api.ondelete(at_uninstall=False)` |
| Batch create      | `create({...})`     | `create([{...}, {...}])`            |
| SQL queries       | `cr.execute()`      | `env.execute_query_dict(SQL(...))`  |

## Bắt đầu nhanh

### Tạo module mới

1. Tạo cấu trúc thư mục:

```
my_module/
├── __init__.py
├── __manifest__.py
├── models/
│   └── my_model.py
├── views/
│   └── my_model_views.xml
└── security/
    └── ir.model.access.csv
```

2. Đọc `odoo-18-development-guide.md` để hiểu về manifest và cấu trúc module

### Viết model hiệu quả

```python
# TỐT: Sử dụng prefetch tự động
orders = self.search([('state', '=', 'done')])
for order in orders:
    print(order.name, order.partner_id.name)  # Partners được fetch theo batch

# XẤU: search trong vòng lặp (N+1 queries)
for order in orders:
    payments = self.env['payment'].search([('order_id', '=', order.id)])

# TỐT: Sử dụng IN domain
payments = self.env['payment'].search_read([('order_id', 'in', orders.ids)])
```

### Decorator quyết định

```
Cần định nghĩa hành vi field?
├── Field tính từ các field khác → @api.depends
├── Validate dữ liệu → @api.constrains
├── Ngăn xóa record → @api.ondelete
└── Update form UI → @api.onchange

Cần định nghĩa hành vi method?
├── Method-level không phụ thuộc self → @api.model
└── Method record bình thường → không cần decorator
```

Xem file `AGENTS.md` trong từng thư mục version để biết hướng dẫn chi tiết cho từng IDE.

- **[Cấu hình cho Odoo 19.0](./19.0/AGENTS.md)**
- **[Cấu hình cho Odoo 18.0](./18.0/AGENTS.md)**

## Nguồn tài liệu

Tất cả các hướng dẫn được dựa trên phân tích mã nguồn Odoo 18 gốc:

- `odoo/models.py` - ORM implementation
- `odoo/fields.py` - Field types
- `odoo/api.py` - Decorators
- `odoo/http.py` - HTTP layer
- `odoo/exceptions.py` - Exception types

## Repository

`git@github.com:unclecatvn/agent-skills.git`

## Giấy phép

MIT License

## Tác giả

UncleCat
