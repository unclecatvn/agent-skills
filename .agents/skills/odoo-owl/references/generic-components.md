# Generic Components

Odoo already ships reusable Owl components in `@web/core`. Prefer them before writing new primitives.

## Common Reusable Components

| Component | Import area | Good fit |
| --- | --- | --- |
| `Dropdown` | `@web/core/dropdown/...` | Menus and option pickers |
| `CheckBox` | `@web/core/checkbox/...` | Simple boolean input |
| `Notebook` | `@web/core/notebook/...` | Tabbed panels |
| `Pager` | `@web/core/pager/...` | Pagination UI |
| `SelectMenu` | `@web/core/select_menu/...` | Searchable or richer selects |
| `TagsList` | `@web/core/tags_list/...` | Tag pills and token lists |
| `ActionSwiper` | `@web/core/action_swiper/...` | Touch swipe actions |

## Selection Rules

- Search the existing addon or `@web/core` before creating a custom equivalent.
- Prefer composition around a generic component instead of cloning its behavior.
- Match the visual and interaction language already used by Odoo screens.
- Only build a custom component when the shipped primitives cannot express the requirement cleanly.
