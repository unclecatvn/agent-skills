# Odoo 18 Development Guides

![npm](https://img.shields.io/badge/npm-%40unclecat--agent--skills--cli-blue?style=flat-square&logo=npm&label=CLI)
![Node](https://img.shields.io/badge/node-%3E%3D18.0.0-green?style=flat-square&logo=node.js)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)

Tài liệu phát triển Odoo 18 toàn diện, bao gồm các hướng dẫn về model, field, decorator, view, performance, controller và best practices.

## Giới thiệu

Đây là bộ tài liệu tham khảo hoàn chỉnh cho phát triển Odoo 18, được tổ chức thành các module nhỏ có thể sử dụng độc lập hoặc kết hợp. Tài liệu dựa trên phân tích mã nguồn Odoo 18 gốc.

## CLI (odoo-cli)

Cài CLI để install nhanh theo version Odoo và AI assistant:

```bash
npm install -g @unclecat/agent-skills-cli
```

### Ví dụ cài theo Odoo 18.0

```bash
# Cursor (tạo .cursor/commands/odoo.md + .shared/odoo/18.0)
agent-skills init --ai cursor odoo --version 18.0

# Claude Code (.claude/skills/odoo/18.0)
agent-skills init --ai claude odoo --version 18.0

# Antigravity (.agent/workflows/odoo.md + .shared/odoo/18.0)
agent-skills init --ai antigravity odoo --version 18.0

# Kiro (.kiro/steering/odoo.md + .shared/odoo/18.0)
agent-skills init --ai kiro odoo --version 18.0

# Lưu full docs vào docs/skills/odoo/18.0
agent-skills init --ai docs odoo --version 18.0

# Cài tất cả
agent-skills init --ai all odoo --version 18.0
```

### Liệt kê version hỗ trợ

```bash
agent-skills versions odoo
```

### Cập nhật CLI

```bash
# Kiểm tra phiên bản mới
agent-skills update

# Cập nhật lên phiên bản mới nhất
npm update -g @unclecat/agent-skills-cli

# Hoặc cài lại bản mới nhất
npm install -g @unclecat/agent-skills-cli@latest
```

> CLI sẽ tự động thông báo khi có phiên bản mới mỗi khi bạn chạy.

## Cấu trúc tài liệu

```
skills/odoo/18.0/
├── SKILL.md                       # File tham khảo chính - tổng quan
├── odoo-18-development-guide.md    # Cấu trúc module, manifest, bảo mật, báo cáo, wizard
├── odoo-18-model-guide.md          # ORM, CRUD, domain, recordset
├── odoo-18-field-guide.md          # Các loại field (Char, Monetary, Many2one, v.v.)
├── odoo-18-decorator-guide.md       # Decorator @api (depends, constrains, onchange, ondelete)
├── odoo-18-view-guide.md           # XML view (list, form, search, kanban), action, menu
├── odoo-18-performance-guide.md    # Ngăn chặn N+1 query, tối ưu hiệu năng
└── odoo-18-controller-guide.md     # HTTP controller, routing, authentication
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

| Thay đổi | Odoo 17 | Odoo 18 |
|----------|---------|---------|
| List view tag | `<tree>` | `<list>` |
| Delete validation | Override `unlink()` | `@api.ondelete(at_uninstall=False)` |
| Batch create | `create({...})` | `create([{...}, {...}])` |
| SQL queries | `cr.execute()` | `env.execute_query_dict(SQL(...))` |

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

## Hướng dẫn cài đặt cho AI IDEs

> **Xem [skills/odoo/18.0/AGENTS.md](skills/odoo/18.0/AGENTS.md)** để biết cách sử dụng tài liệu này với Cursor, Claude Code, OpenCode, GitHub Copilot, v.v.

### Cách nhanh nhất (Cursor - Remote Rules)

1. `Settings` → `Rules` → `Add Remote Rule`
2. URL: `git@github.com:unclecatvn/agent-skills.git`
3. Branch: `odoo/18.0`

Done! Rules tự động áp dụng cho TẤT CẢ projects của bạn.

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
