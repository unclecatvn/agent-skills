#!/usr/bin/env python3
"""Scaffold a standard Odoo Owl component triplet."""

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


def build_js(addon: str, component: str) -> str:
    return f'''/** @odoo-module **/

import {{ Component, useState }} from "@odoo/owl";

export class {component} extends Component {{
    static template = "{addon}.{component}";

    setup() {{
        this.state = useState({{ count: 0 }});
    }}

    increment() {{
        this.state.count++;
    }}
}}
'''


def build_xml(addon: str, component: str, css_class: str) -> str:
    return f'''<?xml version="1.0" encoding="UTF-8" ?>
<templates xml:space="preserve">
    <t t-name="{addon}.{component}">
        <button type="button" class="{css_class}" t-on-click="increment">
            <span>{component}</span>
            <span t-esc="state.count"/>
        </button>
    </t>
</templates>
'''


def build_scss(css_class: str) -> str:
    return f'''.{css_class} {{
    display: inline-flex;
    gap: 0.5rem;
    align-items: center;
}}
'''


def asset_snippet(addon: str, rel_dir: str, stem: str, include_scss: bool, bundle: str) -> str:
    lines = [
        f'"{bundle}": [',
        f'    "{addon}/{rel_dir}/{stem}.js",',
        f'    "{addon}/{rel_dir}/{stem}.xml",',
    ]
    if include_scss:
        lines.append(f'    "{addon}/{rel_dir}/{stem}.scss",')
    lines.append("],")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scaffold an Odoo Owl component.")
    parser.add_argument("--root", required=True, help="Path to the addon root")
    parser.add_argument("--addon", required=True, help="Addon technical name")
    parser.add_argument("--component", required=True, help="Component class name, e.g. PartnerBadge")
    parser.add_argument("--subdir", default="components", help="Subdirectory under static/src")
    parser.add_argument("--bundle", default="web.assets_backend", help="Asset bundle reminder to print")
    parser.add_argument("--with-scss", action="store_true", help="Create an SCSS file")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    addon_root = Path(args.root).resolve()
    if not addon_root.exists():
        print(f"Addon root does not exist: {addon_root}", file=sys.stderr)
        return 1

    stem = to_snake_case(args.component)
    rel_dir = f"static/src/{args.subdir.strip('/').strip()}/{stem}".replace("\\", "/")
    target_dir = addon_root / Path(rel_dir)
    css_class = f"o_{args.addon}_{stem}"

    files = {
        target_dir / f"{stem}.js": build_js(args.addon, args.component),
        target_dir / f"{stem}.xml": build_xml(args.addon, args.component, css_class),
    }
    if args.with_scss:
        files[target_dir / f"{stem}.scss"] = build_scss(css_class)

    try:
        for path, content in files.items():
            write_file(path, content, args.force)
    except FileExistsError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print("Created:")
    for path in files:
        print(f"  {path}")

    print("\nManifest assets snippet:")
    print(asset_snippet(args.addon, rel_dir, stem, args.with_scss, args.bundle))
    print("\nReminders:")
    print("- Keep the template in XML for translation support.")
    print("- Do not move initialization into a constructor; keep it in setup().")
    print("- Confirm the addon actually loads the printed asset bundle.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
