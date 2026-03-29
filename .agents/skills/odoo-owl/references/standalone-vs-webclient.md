# Standalone vs Webclient

## Choose the Integration Model

| Context | Choose when | Notes |
| --- | --- | --- |
| Existing backend screen | The component belongs inside a view, action, or existing web client feature | Reuse the web client environment and services |
| Client action | The component is the root of a navigable backend feature | Use the actions registry; see the extension skill |
| Standalone Owl app | The page owns its own mount target and startup | Build the env explicitly and bundle the app entrypoint |
| Portal or website component | The code runs in frontend website pages rather than the backend | Treat the asset bundle and runtime context separately |

## Practical Rule

If the user asks for a reusable component or a fix inside an existing addon screen, stay close to the addon's current structure. If the request describes a brand-new backend screen or app entrypoint, re-evaluate whether a client action or standalone app is the better fit.

## Handoff Rule

- Switch to `odoo-webclient-extension` when the decision requires registries, actions, services, or patches.
- Switch to `odoo-owl-testing` once the main deliverable becomes tests instead of production code.
