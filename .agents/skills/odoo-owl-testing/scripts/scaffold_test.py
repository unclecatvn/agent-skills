#!/usr/bin/env python3
"""Scaffold a starter Odoo frontend test file."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def to_snake_case(value: str) -> str:
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value)
    value = re.sub(r"[^A-Za-z0-9]+", "_", value)
    return value.strip("_").lower()


def ensure_can_write(path: Path, force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"Refusing to overwrite existing file: {path}")


def write_file(path: Path, content: str, force: bool) -> None:
    ensure_can_write(path, force)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_component_test(addon: str, label: str) -> str:
    return f'''/** @odoo-module **/

import {{ Component, xml }} from "@odoo/owl";
import {{ describe, expect, test }} from "@odoo/hoot";
import {{ mountWithCleanup }} from "@web/../tests/web_test_helpers";

class PlaceholderComponent extends Component {{
    static template = xml`<div class="o_test_root">{label}</div>`;
}}

describe("{addon}: {label}", () => {{
    test("mounts a placeholder component", async () => {{
        await mountWithCleanup(PlaceholderComponent);

        expect(".o_test_root").toHaveText("{label}");
    }});
}});
'''


def build_service_test(addon: str, label: str) -> str:
    return f'''/** @odoo-module **/

import {{ describe, expect, test }} from "@odoo/hoot";
import {{ makeMockEnv }} from "@web/../tests/web_test_helpers";

describe("{addon}: {label}", () => {{
    test("starts a mock environment", async () => {{
        const env = await makeMockEnv();

        expect(Boolean(env)).toBe(true);
    }});
}});
'''


def build_view_test(addon: str, label: str) -> str:
    return f'''/** @odoo-module **/

import {{ describe, expect, test }} from "@odoo/hoot";

describe("{addon}: {label}", () => {{
    test("replace with a mountView-based test", async () => {{
        expect(true).toBe(true);
    }});
}});
'''


def build_test(kind: str, addon: str, label: str) -> str:
    if kind == "component":
        return build_component_test(addon, label)
    if kind == "service":
        return build_service_test(addon, label)
    return build_view_test(addon, label)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scaffold an Odoo frontend test file.")
    parser.add_argument("--root", required=True, help="Path to the addon root")
    parser.add_argument("--addon", required=True, help="Addon technical name")
    parser.add_argument("--name", required=True, help="Short test name, e.g. partner_badge")
    parser.add_argument(
        "--kind",
        choices=["component", "service", "view"],
        default="component",
        help="Starter template shape",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite an existing file")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    addon_root = Path(args.root).resolve()
    if not addon_root.exists():
        print(f"Addon root does not exist: {addon_root}", file=sys.stderr)
        return 1

    stem = to_snake_case(args.name)
    test_path = addon_root / "static" / "tests" / f"{stem}.test.js"
    label = stem.replace("_", " ")

    try:
        write_file(test_path, build_test(args.kind, args.addon, label), args.force)
    except FileExistsError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"Created: {test_path}")
    print("\nManifest assets snippet:")
    print('"web.assets_unit_tests": [')
    print(f'    "{args.addon}/static/tests/**/*",')
    print("],")
    print("\nReminders:")
    print("- Keep test files under static/tests and end them with .test.js.")
    print("- Replace the placeholder logic with the real unit under test.")
    print("- Add mock models before expecting ORM-backed behavior to work.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
