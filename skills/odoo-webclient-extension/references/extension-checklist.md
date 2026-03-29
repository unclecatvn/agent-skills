# Extension Checklist

Before editing:

- Identify the target addon, bundle, and runtime context.
- Search for existing registry categories and extension points.
- Search for an existing service or component you can reuse.

When implementing:

- Namespace keys, tags, and template names with the addon name.
- Keep JS/XML/SCSS files colocated.
- Wire assets and data files in the manifest.
- Prefer `useService()` and official hooks in components.

Before finishing:

- Confirm the action tag matches the server-side `ir.actions.client` record.
- Confirm the registry category is correct.
- Confirm patching was truly necessary.
- Confirm the addon still follows the surrounding web client conventions.
