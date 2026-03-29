# Testing Checklist

Before writing the test:

- Identify whether the unit is a component, service, or view.
- Confirm the addon path and import path.
- Confirm the proper helper: `makeMockEnv`, `mountWithCleanup`, or `mountView`.

While writing the test:

- Keep the test under `static/tests`.
- Keep the filename ending in `.test.js`.
- Add mock models before expecting ORM calls to work.
- Prefer DOM assertions over internal state assertions.

Before finishing:

- Confirm the folder is included in `web.assets_unit_tests`.
- Confirm the test can run from `/web/tests`.
- Confirm the failure message would help a future maintainer.
