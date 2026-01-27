---
name: odoo-18-owl
description: Complete reference for Odoo 18 OWL (Owl Web Library) components, hooks, services, and patterns for building interactive JavaScript UI components.
globs: "**/static/src/**/*.js"
topics:
  - OWL basics (Component, setup, template, props, state)
  - OWL hooks (useState, useEffect, onMounted, onWillUnmount, useRef, useService)
  - Odoo components (Dropdown, SelectMenu, TagsList, Notebook, Pager, CheckBox, ColorList, ActionSwiper)
  - Services (rpc, dialog, notification, ui, action, router)
  - QWeb templates and directives
  - Registries (category, add, get, contains)
  - Assets and module structure
when_to_use:
  - Creating custom UI components
  - Building views and widgets
  - Implementing client actions
  - Creating frontend interactions
  - Extending existing components
---

# Odoo 18 OWL Guide

Complete reference for Odoo 18 OWL (Owl Web Library) components, hooks, services, and patterns for building interactive JavaScript UI components.

## Table of Contents

1. [OWL Basics](#owl-basics)
2. [Component Lifecycle](#component-lifecycle)
3. [OWL Hooks](#owl-hooks)
4. [Odoo Core Components](#odoo-core-components)
5. [Services](#services)
6. [QWeb Templates](#qweb-templates)
7. [Registries](#registries)
8. [RPC and Data](#rpc-and-data)
9. [Common Patterns](#common-patterns)
10. [Best Practices](#best-practices)

---

## OWL Basics

### Import OWL from @odoo/owl

```javascript
import {
    Component,
    xml,
    useState,
    useEffect,
    onMounted,
    onWillUnmount,
    useRef,
    useSubEnv
} from "@odoo/owl";
```

### Basic Component Structure

```javascript
import { Component, xml, useState } from "@odoo/owl";

export class MyComponent extends Component {
    // Static properties define component metadata
    static template = xml`
        <div class="my-component" t-on-click="increment">
            <span t-esc="state.value"/>
        </div>
    `;

    static components = {}; // Child components

    static props = {
        value: { type: Number, optional: true },
        onValueChange: { type: Function, optional: true },
    };

    static defaultProps = {
        value: 0,
    };

    // setup() is called once when component is created
    setup() {
        this.state = useState({ value: this.props.value || 0 });
    }

    increment() {
        this.state.value++;
        if (this.props.onValueChange) {
            this.props.onValueChange(this.state.value);
        }
    }
}
```

### Template in XML File (Recommended)

**JavaScript file (`my_component.js`)**:
```javascript
import { Component, useState } from "@odoo/owl";

export class MyComponent extends Component {
    static template = "myaddon.MyComponent";
    static props = ["*"];

    setup() {
        this.state = useState({ count: 0 });
    }

    increment() {
        this.state.count++;
    }
}
```

**XML template file (`my_component.xml`)**:
```xml
<?xml version="1.0" encoding="UTF-8" ?>
<templates xml:space="preserve">
    <t t-name="myaddon.MyComponent">
        <div class="my-component">
            <button t-on-click="increment">
                Count: <t t-esc="state.count"/>
            </button>
        </div>
    </t>
</templates>
```

**Important**: Template names should follow the convention `addon_name.ComponentName`.

### File Structure

A typical OWL component in Odoo should have these files in the same directory:

```
static/src/views/my_module/
├── my_component.js       # Component logic
├── my_component.xml      # QWeb template
└── my_component.scss     # Styles (optional)
```

Add to assets bundle in `__manifest__.py`:

```python
'assets': {
    'web.assets_backend': [
        'my_module/static/src/views/my_module/**/*.js',
        'my_module/static/src/views/my_module/**/*.xml',
        'my_module/static/src/views/my_module/**/*.scss',
    ],
}
```

---

## Component Lifecycle

### Lifecycle Order

```javascript
import {
    Component,
    setup,
    onMounted,
    onWillStart,
    onWillUnmount,
    onWillUpdateProps,
    onWillPatch,
    onPatched,
    onRendered
} from "@odoo/owl";

class LifecycleDemo extends Component {
    setup() {
        // 1. Called first - component initialization
        console.log("setup");

        // 2. Called before first render
        onWillStart(() => {
            console.log("onWillStart");
            // Async setup: load data, start services
            return this.loadData();
        });

        // 3. Called after DOM is mounted
        onMounted(() => {
            console.log("onMounted");
            // DOM access, animations, third-party libs
        });

        // 4. Called before props update
        onWillUpdateProps((nextProps) => {
            console.log("onWillUpdateProps", nextProps);
        });

        // 5. Called before DOM patch
        onWillPatch(() => {
            console.log("onWillPatch");
        });

        // 6. Called after DOM patch
        onPatched(() => {
            console.log("onPatched");
        });

        // 7. Called after each render
        onRendered(() => {
            console.log("onRendered");
        });

        // 8. Called before component unmount
        onWillUnmount(() => {
            console.log("onWillUnmount");
            // Cleanup: remove listeners, cancel timers
        });
    }
}
```

### Setup Method (Best Practice)

**Always use `setup()` instead of `constructor`**:

```javascript
// CORRECT
class GoodComponent extends Component {
    setup() {
        this.state = useState({ value: 1 });
    }
}

// INCORRECT - Do not use constructor
class BadComponent extends Component {
    constructor(parent, props) {
        super(parent, props);
        this.state = useState({ value: 1 });
    }
}
```

**Why**: `setup()` is overridable, constructor is not. Odoo needs to extend component behavior.

---

## OWL Hooks

### useState - Reactive State

```javascript
import { useState } from "@odoo/owl";

setup() {
    // Simple state
    this.state = useState({
        count: 0,
        name: "Test"
    });

    // Nested state
    this.state = useState({
        user: {
            name: "John",
            email: "john@example.com"
        },
        settings: {
            theme: "dark"
        }
    });

    // Access and modify
    this.state.count++;      // Triggers re-render
    this.state.user.name = "Jane";  // Also reactive
}
```

### useEffect - Side Effects

```javascript
import { useEffect, useState } from "@odoo/owl";

setup() {
    this.state = useState({ count: 0 });

    // Run when count changes
    useEffect(
        () => {
            document.title = `Count: ${this.state.count}`;
        },
        () => [this.state.count]  // Dependency function
    );

    // Cleanup on unmount or dependency change
    useEffect(
        () => {
            const timer = setInterval(() => {
                console.log("tick");
            }, 1000);
            return () => clearInterval(timer);
        },
        () => []
    );
}
```

### useRef - DOM References

```javascript
import { useRef, onMounted } from "@odoo/owl";

setup() {
    this.inputRef = useRef("inputRef");

    onMounted(() => {
        // Access DOM element
        this.inputRef.el.focus();
        this.inputRef.el.value = "Hello";
    });
}

// In template:
// <input t-ref="inputRef" />
```

### useService - Access Odoo Services

```javascript
import { useService } from "@web/core/utils/hooks";

setup() {
    // RPC service - call Python methods
    this.rpc = useService("rpc");

    // Dialog service - show modals
    this.dialog = useService("dialog");

    // Notification service - show toasts
    this.notification = useService("notification");

    // Router service - navigation
    this.router = useService("router");

    // Action service - execute Odoo actions
    this.action = useService("action");

    // UI service - UI state
    this.ui = useService("ui");

    // ORM service - database operations
    this.orm = useService("orm");
}
```

### useSubEnv - Nested Environment

```javascript
import { useSubEnv } from "@odoo/owl";

setup() {
    // Override environment for child components
    useSubEnv({
        customProp: "value",
        model: this.props.record.model,
    });
}
```

---

## Odoo Core Components

### Dropdown - Full-Featured Dropdown

```javascript
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";

static components = { Dropdown, DropdownItem };

static template = xml`
    <Dropdown>
        <button class="btn btn-primary">Options</button>
        <t t-set-slot="content">
            <DropdownItem onSelected="() => this.doAction('edit')">
                Edit
            </DropdownItem>
            <DropdownItem onSelected="() => this.doAction('delete')">
                Delete
            </DropdownItem>
            <DropdownItem onSelected="() => this.doAction('archive')" closingMode="'none'">
                Archive (keep open)
            </DropdownItem>
        </t>
    </Dropdown>
`;
```

**Nested Dropdown**:
```xml
<Dropdown>
    <button>File</button>
    <t t-set-slot="content">
        <DropdownItem onSelected="save">Save</DropdownItem>
        <Dropdown>
            <button>New</button>
            <t t-set-slot="content">
                <DropdownItem onSelected="newDocument">Document</DropdownItem>
                <DropdownItem onSelected="newSpreadsheet">Spreadsheet</DropdownItem>
            </t>
        </Dropdown>
    </t>
</Dropdown>
```

**Dropdown Props**:
| Prop | Type | Description |
|------|------|-------------|
| `menuClass` | `String` | Optional classname for menu |
| `disabled` | `Boolean` | Disable dropdown |
| `position` | `String` | Menu position (default: `bottom-start`) |
| `beforeOpen` | `Function` | Called before opening (async ok) |
| `onOpened` | `Function` | Called after opening |
| `manual` | `Boolean` | Don't add click handlers (use with `state`) |

### SelectMenu - Enhanced Select

```javascript
import { SelectMenu } from "@web/core/select_menu/select_menu";

static components = { SelectMenu };

static template = xml`
    <SelectMenu
        choices="choices"
        value="state.selectedValue"
        onSelect="onSelect"
        searchable="true"
    />
`;

get choices() {
    return [
        { value: "1", label: "Option 1" },
        { value: "2", label: "Option 2" },
        { value: "3", label: "Option 3" },
    ];
}

onSelect(value) {
    this.state.selectedValue = value;
}
```

**Multi-Select with Groups**:
```xml
<SelectMenu
    choices="choices"
    groups="groups"
    multiSelect="true"
    value="state.selectedValues"
>
    <span>Select items</span>
    <t t-set-slot="choice" t-slot-scope="choice">
        <span t-esc="'👉 ' + choice.data.label + ' 👈'" />
    </t>
</SelectMenu>
```

**SelectMenu Props**:
| Prop | Type | Description |
|------|------|-------------|
| `choices` | `Array` | List of `{value, label}` |
| `groups` | `Array` | Grouped choices |
| `multiSelect` | `Boolean` | Enable multiple selection |
| `searchable` | `Boolean` | Show search box |
| `value` | `any` | Selected value(s) |
| `onSelect` | `Function` | Callback on selection |

### TagsList - Display Tags

```javascript
import { TagsList } from "@web/core/tags_list/tags_list";

static template = xml`
    <TagsList tags="state.tags" />
`;

get state() {
    return {
        tags: [
            { id: "tag1", text: "Earth", colorIndex: 1 },
            {
                id: "tag2",
                text: "Wind",
                colorIndex: 2,
                onDelete: () => this.deleteTag("tag2")
            },
            {
                id: "tag3",
                text: "Fire",
                icon: "fa-fire",
                onClick: () => this.clickTag("tag3"),
                onDelete: () => this.deleteTag("tag3")
            },
        ]
    };
}
```

**Color IDs**: 0 (No color), 1 (Red), 2 (Orange), 3 (Yellow), 4 (Light blue), 5 (Dark purple), 6 (Salmon pink), 7 (Medium blue), 8 (Dark blue), 9 (Fuchsia), 11 (Purple), 12 (Green)

### Notebook - Tabbed Interface

```javascript
import { Notebook } from "@web/core/notebook/notebook";

static template = xml`
    <Notebook orientation="'vertical'" defaultPage="'page_2'">
        <t t-set-slot="page_1" title="'First Page'" isVisible="true">
            <h1>Page 1 Content</h1>
        </t>
        <t t-set-slot="page_2" title="'Second Page'" isVisible="true">
            <p>Page 2 Content</p>
        </t>
    </Notebook>
`;
```

**Programmatic Pages**:
```javascript
get pages() {
    return [
        {
            Component: MyTemplateComponent,
            id: "page_1",
            title: "Page 1",
            props: { title: "My First Page" },
            isDisabled: false,
        },
        {
            Component: MyTemplateComponent,
            id: "page_2",
            title: "Page 2",
            props: { title: "My Second Page" },
        },
    ];
}
```

### Pager - Pagination

```javascript
import { Pager } from "@web/core/pager/pager";

static template = xml`
    <Pager
        offset="state.offset"
        limit="state.limit"
        total="state.total"
        onUpdate="onPageUpdate"
    />
`;

setup() {
    this.state = useState({
        offset: 0,
        limit: 80,
        total: 200,
    });
}

onPageDownload({ offset, limit }) {
    this.state.offset = offset;
    this.state.limit = limit;
    this.loadRecords();
}
```

**Display**: "1-80 / 200" (offset is 0-based, displayed as 1-based)

### CheckBox - Simple Checkbox

```javascript
import { CheckBox } from "@web/core/checkbox/checkbox";

static template = xml`
    <CheckBox
        value="state.isChecked"
        disabled="state.isDisabled"
        t-on-change="onCheckboxChange"
    >
        Agree to terms
    </CheckBox>
`;
```

### ColorList - Color Picker

```javascript
import { ColorList } from "@web/core/colorlist/colorlist";

static template = xml`
    <ColorList
        colors="state.availableColors"
        selectedColor="state.selectedColorId"
        onColorSelected="onColorSelected"
        canToggle="true"
    />
`;
```

### ActionSwiper - Touch Swipe Actions

```javascript
import { ActionSwiper } from "@web/core/action_swiper/action_swiper";

static template = xml`
    <ActionSwiper
        onLeftSwipe="swipeLeftAction"
        onRightSwipe="swipeRightAction"
        swipeDistanceRatio="0.3"
    >
        <div>Swipeable item</div>
    </ActionSwiper>
`;

get swipeLeftAction() {
    return {
        action: () => this.deleteItem(),
        icon: 'fa-delete',
        bgColor: 'bg-danger',
    };
}

get swipeRightAction() {
    return {
        action: () => this.starItem(),
        icon: 'fa-star',
        bgColor: 'bg-warning',
    };
}
```

---

## Services

### RPC Service - Call Python Methods

```javascript
this.rpc = useService("rpc");

// Simple call
const result = await this.rpc("/my/controller/endpoint", { arg1: "value" });

// Model method call
const partners = await this.rpc({
    model: "res.partner",
    method: "search_read",
    args: [[["is_company", "=", true]]],
    kwargs: { fields: ["name", "email"] },
});

// Named route with params
const data = await this.rpc("/web/dataset/call_kw", {
    model: "sale.order",
    method: "action_confirm",
    args: [[orderId]],
});
```

### ORM Service - Database Operations

```javascript
this.orm = useService("orm");

// Read records
const records = await this.orm.searchRead(
    "res.partner",
    [["customer_rank", ">", 0]],
    ["name", "email", "phone"]
);

// Create record
const id = await this.orm.create("res.partner", [{
    name: "New Partner",
    email: "test@example.com",
}]);

// Write records
await this.orm.write("res.partner", [id], {
    phone: "123456"
});

// Unlink records
await this.orm.unlink("res.partner", [id]);

// Call method
const result = await this.orm.call("res.partner", "name_get", [[id]]);

// Read group
const groups = await this.orm.readGroup(
    "sale.order",
    [["state", "!=", "draft"]],
    ["state", "amount_total:sum"],
    ["state"]
);
```

### Dialog Service - Show Modals

```javascript
this.dialog = useService("dialog");

// Simple dialog
this.dialog.add(MyDialogComponent, {
    title: "Confirmation",
    message: "Are you sure?",
    confirm: () => this.doAction(),
});

// Confirm dialog
this.dialog.add(ConfirmationDialog, {
    title: this.env._t("Delete Record"),
    body: this.env._t("Are you sure you want to delete this record?"),
    confirm: async () => {
        await this.orm.unlink(this.props.resModel, [this.props.resId]);
        this.props.close();
    },
    cancel: () => {},
});
```

### Notification Service - Toast Messages

```javascript
this.notification = useService("notification");

// Simple notification
this.notification.notify("Message sent!", { type: "success" });

// With options
this.notification.notify("Error occurred", {
    type: "danger",
    sticky: true,
    title: "Error",
});

// Types: success, info, warning, danger
```

### Action Service - Execute Odoo Actions

```javascript
this.action = useService("action");

// Execute window action
await this.action.doAction({
    name: "Partners",
    type: "ir.actions.act_window",
    res_model: "res.partner",
    view_mode: "tree,form",
    views: [[false, "list"], [false, "form"]],
    domain: [["customer_rank", ">", 0]],
});

// Open form
await this.action.doAction({
    type: "ir.actions.act_window",
    res_model: "res.partner",
    res_id: partnerId,
    views: [[false, "form"]],
    target: "new",  // or "current", "fullscreen"
});

// Reload current action
await this.action.reload();

// Back button
await this.action.doBack();
```

### Router Service - Navigation

```javascript
this.router = useService("router");

// Navigate to action
this.router.push({ action: 123 });

// Navigate with search domain
this.router.push({
    action: 123,
    view_type: "list",
    model: "sale.order",
    domain: '[["state", "=", "draft"]]',
});

// Get current state
const state = this.router.current;
```

### UI Service - UI State

```javascript
this.ui = useService("ui");

// Check if small screen (mobile)
const isSmall = this.ui.isSmall;

// Check if active element
const isActive = this.ui.isActiveElement(element);

// Block/Unblock UI
this.ui.block();
try {
    await someOperation();
} finally {
    this.ui.unblock();
}
```

### Registry Service

```javascript
this.registry = useService("registry");

// Get category
const viewRegistry = registry.category("views");

// Add to registry
viewRegistry.add("my_view", {
    ...myViewDefinition,
});

// Get from registry
const viewDef = viewRegistry.get("my_view");

// Check existence
if (viewRegistry.contains("my_view")) {
    // ...
}

// Remove from registry
viewRegistry.remove("my_view");

// Get all
const allViews = viewRegistry.getAll();
```

---

## QWeb Templates

### Template Directives

```xml
<!-- Render value -->
<t t-esc="state.value" />

<!-- Render HTML (unsafe) -->
<t t-raw="state.htmlContent" />

<!-- Conditionals -->
<div t-if="state.isActive">Active</div>
<div t-elif="state.isPending">Pending</div>
<div t-else="">Inactive</div>

<!-- Loops -->
<t t-foreach="state.records" t-as="record" t-key="record.id">
    <span t-attf-class="record-{{record.id}}">
        <t t-esc="record.name" />
    </span>
</t>

<!-- Attributes -->
<input t-att-value="state.value" />
<input t-attf-placeholder="Search {{state.modelName}}" />
<div t-att-class="state.isActive ? 'active' : ''" />
<div t-att="{'data-id': record.id, 'data-name': record.name}" />

<!-- Event handlers -->
<button t-on-click="handleClick">Click</button>
<input t-on-input="onInput" />
<div t-on-mouseenter="onHover" />

<!-- Set variable -->
<t t-set="userName" t-value="record.name" />
<t t-foreach="items" t-as="item">
    <t t-set="index" t-value="index + 1" />
</t>

<!-- Call template -->
<t t-call="myaddon.OtherTemplate">
    <t t-set="customProp" t-value="'custom'" />
</t>

<!-- Debug -->
<t t-debug="state" />
```

### Inline XML Templates

```javascript
static template = xml`
    <div class="my-component">
        <h1 t-esc="props.title"/>
        <input
            t-model="state.searchText"
            t-on-input="onSearchInput"
            placeholder="Search..."
        />
        <ul>
            <li t-foreach="state.filteredItems" t-as="item" t-key="item.id">
                <span t-esc="item.name" />
                <button t-on-click="() => this.selectItem(item)">
                    Select
                </button>
            </li>
        </ul>
    </div>
`;
```

---

## Registries

### Using Registries

```javascript
import { registry } from "@web/core/registry";

// Get or create category
const viewRegistry = registry.category("views");
const fieldRegistry = registry.category("fields");
const actionRegistry = registry.category("actions");

// Add to registry
viewRegistry.add("my_custom_view", {
    type: "my_custom_view",
    display_name: "My Custom View",
    icon: "fa-star",
    isMobileFriendly: true,
    Controller: MyViewController,
    Renderer: MyViewRenderer,
    Model: MyViewModel,
});

// Get from registry
const viewDef = viewRegistry.get("my_custom_view");

// Check if contains
if (viewRegistry.contains("my_custom_view")) {
    console.log("View registered!");
}

// Add multiple
viewRegistry.add("view1", view1Def);
viewRegistry.add("view2", view2Def);

// Remove
viewRegistry.remove("view1");

// Get all
const allViews = viewRegistry.getAll();

// Add with validation
fieldRegistry.add("custom.field", {
    component: CustomField,
    supportedTypes: ["char", "text"],
    extractProps: (fieldInfo, props) => {
        return {
            maxLength: fieldInfo.rawAttrs.maxlength,
        };
    },
}, {
    // Validate
    component: (c) => c.prototype instanceof Component,
    supportedTypes: { type: Array, element: String },
});
```

---

## RPC and Data

### Common Data Patterns

```javascript
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class DataComponent extends Component {
    static template = "myaddon.DataComponent";
    static props = ["*"];

    setup() {
        this.orm = useService("orm");
        this.rpc = useService("rpc");

        this.state = useState({
            records: [],
            isLoading: false,
            error: null,
        });

        onWillStart(this.onWillStart);
    }

    async onWillStart() {
        await this.loadRecords();
    }

    async loadRecords() {
        this.state.isLoading = true;
        this.state.error = null;

        try {
            this.state.records = await this.orm.searchRead(
                "res.partner",
                [["customer_rank", ">", 0]],
                ["name", "email", "phone"],
                { limit: 100 }
            );
        } catch (error) {
            this.state.error = error.message;
        } finally {
            this.state.isLoading = false;
        }
    }
}
```

### Custom RPC Methods

```javascript
// In Python controller
@http.route('/my/custom/endpoint', type='json', auth='user')
def custom_endpoint(self, **kwargs):
    records = request.env['my.model'].search_read(
        [('state', '=', 'active')],
        ['name', 'value']
    )
    return {
        'records': records,
        'count': len(records),
    }

// In JavaScript
async callCustomEndpoint() {
    const result = await this.rpc("/my/custom/endpoint", {
        search_domain: [["state", "=", "active"]],
    });
    this.state.records = result.records;
    this.state.count = result.count;
}
```

---

## Common Patterns

### Props Definition

```javascript
static props = {
    // Required prop
    record: Object,

    // Optional prop
    title: { type: String, optional: true },

    // Union type
    value: { type: [String, Number], optional: true },

    // Wildcard (accept any)
    custom: "*",

    // Array type
    items: {
        type: Array,
        element: Object,
        shape: {
            id: Number,
            name: String,
        },
    },

    // Function prop
    onUpdate: { type: Function, optional: true },
};

static defaultProps = {
    title: "Default Title",
    items: [],
};
```

### Slots

```javascript
// Parent component
static template = xml`
    <div class="parent">
        <h2>Default slot content:</h2>
        <div class="default-slot">
            <t t-slot="default" />
        </div>

        <h2>Named slot:</h2>
        <div class="header-slot">
            <t t-slot="header" />
        </div>

        <h2>Scoped slot:</h2>
        <div class="scoped-slot">
            <t t-slot="item" t-slot-scope="item">
                <span t-esc="item.data.name" />
            </t>
        </div>
    </div>
`;

// Child usage
static template = xml`
    <ParentComponent>
        <!-- Default slot -->
        <div>Default content</div>

        <!-- Named slot -->
        <t t-set-slot="header">
            <h1>Custom Header</h1>
        </t>

        <!-- Scoped slot -->
        <t t-set-slot="item" t-slot-scope="item">
            <span>👉 <t t-esc="item.data.name" /> 👈</span>
        </t>
    </ParentComponent>
`;
```

### Event Handling

```javascript
// Template
static template = xml`
    <div>
        <button t-on-click="handleClick">Click</button>
        <input t-on-input="onInput" />
        <form t-on-submit="onSubmit">
            <button type="submit">Submit</button>
        </form>
    </div>
`;

// Handlers
handleClick(ev) {
    console.log("Clicked!", ev.target);
    ev.stopPropagation();
}

onInput(ev) {
    const value = ev.target.value;
    this.state.searchTerm = value;
}

async onSubmit(ev) {
    ev.preventDefault();
    await this.save();
}
```

### Environment Access

```javascript
setup() {
    // Access env props
    this.model = this.env.model;
    this.resModel = this.env.resModel;
    this.resId = this.env.resId;

    // Translation
    const _t = this.env._t;
    this.message = _t("Hello World");

    // Provide to children
    useSubEnv({
        customProp: "value",
        parentComponent: this,
    });
}
```

---

## Best Practices

### DO ✓

1. **Use `setup()` instead of `constructor`**
   ```javascript
   setup() {
       this.state = useState({ value: 1 });
   }
   ```

2. **Define templates in XML files**
   ```javascript
   static template = "myaddon.MyComponent";
   ```

3. **Use proper template naming**
   ```javascript
   // Convention: addon_name.ComponentName
   static template = "myaddon.MyComponent";
   ```

4. **Define props explicitly**
   ```javascript
   static props = {
       record: Object,
       title: { type: String, optional: true },
   };
   ```

5. **Clean up in `onWillUnmount`**
   ```javascript
   onWillUnmount(() => {
       this.observer.disconnect();
       clearInterval(this.timer);
   });
   ```

6. **Use services for cross-cutting concerns**
   ```javascript
   this.rpc = useService("rpc");
   this.orm = useService("orm");
   this.dialog = useService("dialog");
   ```

7. **Prefer native HTML elements when possible**
   ```javascript
   // Use native select for simple cases
   <select t-model="state.value">
       <option value="1">Option 1</option>
   </select>
   ```

### DON'T ✗

1. **Don't use `constructor`**
   ```javascript
   // BAD
   constructor(parent, props) {
       super(parent, props);
   }
   ```

2. **Don't inline templates for production**
   ```javascript
   // BAD (except for simple components)
   static template = xml`<div>...</div>`;
   ```

4. **Don't use `*` for props unless necessary**
   ```javascript
   // BAD - use explicit props
   static props = ["*"];
   ```

5. **Don't forget cleanup**
   ```javascript
   // BAD - memory leak
   setup() {
       this.timer = setInterval(() => {}, 1000);
   }
   ```

6. **Don't manipulate DOM directly**
   ```javascript
   // BAD
   setup() {
       document.querySelector(".my-element").style.display = "none";
   }

   // GOOD - use refs and lifecycle
   onMounted(() => {
       if (this.myRef.el) {
           this.myRef.el.style.display = "none";
       }
   });
   ```

---

## Complete Component Example

```javascript
/** @odoo-module **/
import { Component, xml, useState, onMounted, useRef, onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { TagsList } from "@web/core/tags_list/tags_list";

export class PartnerList extends Component {
    static template = "myaddon.PartnerList";
    static components = { Dropdown, DropdownItem, TagsList };

    static props = {
        domain: { type: Array, optional: true },
        limit: { type: Number, optional: true },
    };

    static defaultProps = {
        domain: [],
        limit: 80,
    };

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");

        this.state = useState({
            partners: [],
            selectedPartners: new Set(),
            isLoading: false,
            searchValue: "",
        });

        this.rootRef = useRef("root");

        onMounted(() => this.loadPartners());
    }

    get filteredPartners() {
        if (!this.state.searchValue) {
            return this.state.partners;
        }
        const search = this.state.searchValue.toLowerCase();
        return this.state.partners.filter(p =>
            p.name.toLowerCase().includes(search)
        );
    }

    get tags() {
        return Array.from(this.state.selectedPartners).map(id => {
            const partner = this.state.partners.find(p => p.id === id);
            return {
                id: id.toString(),
                text: partner ? partner.name : `#${id}`,
                colorIndex: 1,
                onDelete: () => this.togglePartner(id),
            };
        });
    }

    async loadPartners() {
        this.state.isLoading = true;
        try {
            this.state.partners = await this.orm.searchRead(
                "res.partner",
                this.props.domain,
                ["name", "email", "phone"],
                { limit: this.props.limit }
            );
        } catch (error) {
            this.notification.notify("Failed to load partners", { type: "danger" });
        } finally {
            this.state.isLoading = false;
        }
    }

    togglePartner(id) {
        if (this.state.selectedPartners.has(id)) {
            this.state.selectedPartners.delete(id);
        } else {
            this.state.selectedPartners.add(id);
        }
        // Trigger reactivity
        this.state.selectedPartners = new Set(this.state.selectedPartners);
    }

    onSearchInput(ev) {
        this.state.searchValue = ev.target.value;
    }

    async doAction(action) {
        const ids = Array.from(this.state.selectedPartners);
        if (!ids.length) {
            this.notification.notify("No partners selected", { type: "warning" });
            return;
        }

        try {
            if (action === "archive") {
                await this.orm.write("res.partner", ids, { active: false });
                this.notification.notify(`${ids.length} partners archived`, { type: "success" });
            } else if (action === "delete") {
                await this.orm.unlink("res.partner", ids);
                this.notification.notify(`${ids.length} partners deleted`, { type: "success" });
            }
            this.state.selectedPartners = new Set();
            await this.loadPartners();
        } catch (error) {
            this.notification.notify("Action failed", { type: "danger" });
        }
    }
}
```

**XML Template (`partner_list.xml`)**:
```xml
<?xml version="1.0" encoding="UTF-8" ?>
<templates xml:space="preserve">
    <t t-name="myaddon.PartnerList">
        <div class="partner-list" t-ref="root">
            <!-- Tags for selected partners -->
            <TagsList tags="tags" />

            <!-- Search and actions -->
            <div class="d-flex justify-content-between mb-3">
                <input
                    type="text"
                    class="form-control"
                    placeholder="Search partners..."
                    t-model="state.searchValue"
                    t-on-input="onSearchInput"
                />
                <Dropdown>
                    <button class="btn btn-primary">Actions</button>
                    <t t-set-slot="content">
                        <DropdownItem onSelected="() => this.doAction('archive')">
                            Archive
                        </DropdownItem>
                        <DropdownItem onSelected="() => this.doAction('delete')">
                            Delete
                        </DropdownItem>
                    </t>
                </Dropdown>
            </div>

            <!-- Loading state -->
            <div t-if="state.isLoading" class="text-center">
                <i class="fa fa-spinner fa-spin" />
            </div>

            <!-- Partner list -->
            <div class="list-group">
                <t t-foreach="filteredPartners" t-as="partner" t-key="partner.id">
                    <div
                        class="list-group-item d-flex justify-content-between align-items-center"
                        t-att-class="state.selectedPartners.has(partner.id) ? 'active' : ''"
                        t-on-click="() => this.togglePartner(partner.id)"
                    >
                        <div>
                            <strong t-esc="partner.name" />
                            <div t-if="partner.email" class="text-muted">
                                <t t-esc="partner.email" />
                            </div>
                        </div>
                        <i class="fa fa-check" t-if="state.selectedPartners.has(partner.id)" />
                    </div>
                </t>
            </div>
        </div>
    </t>
</templates>
```

---

## Key Takeaways

1. **Always use `setup()` method** instead of `constructor` for initialization
2. **Templates should be in XML files** following `addon_name.ComponentName` convention
3. **Use hooks for reactivity**: `useState`, `useEffect`, `useRef`, `useService`
4. **Leverage Odoo services**: `rpc`, `orm`, `dialog`, `notification`, `action`
5. **Use core components**: `Dropdown`, `SelectMenu`, `TagsList`, `Notebook`, `Pager`
6. **Define props explicitly** with proper types and optional flags
7. **Clean up resources** in `onWillUnmount`
8. **Prefer native elements** over complex components when possible
