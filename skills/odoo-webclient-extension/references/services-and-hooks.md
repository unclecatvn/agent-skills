# Services and Hooks

## Choose Service vs Component State

Use component-local state when the data is short-lived and owned by one component. Use a service when the behavior is shared, long-lived, or needed outside component lifecycles.

## Component Access

Inside a component, prefer `useService()`:

```js
import { useService } from "@web/core/utils/hooks";

setup() {
    this.orm = useService("orm");
}
```

## Useful Odoo Hooks

- `useService()` for services such as `orm`, `rpc`, `action`, or `notification`
- `useBus()` for bus-driven subscriptions
- `useAssets()` when lazy asset loading is necessary

## Server Interaction Rule

- Use the `orm` service to call model methods.
- Use the `rpc` service for controller routes.
- Keep network and cross-component coordination out of random component helpers when a service expresses the behavior more clearly.
