#!/usr/bin/env python3
"""Scaffold an Odoo client action with registry and data snippets."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def to_snake_case(value: str) -> str:
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value)
    value = re.sub(r"[^A-Za-z0-9]+", "_", value)
    return value.strip("_").lower()


def titleize(value: str) -> str:
    parts = re.findall(r"[A-Z]?[a-z0-9]+|[A-Z]+(?![a-z])", value)
    return " ".join(parts) if parts else value


def ensure_can_write(path: Path, force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"Refusing to overwrite existing file: {path}")


def write_file(path: Path, content: str, force: bool) -> None:
    ensure_can_write(path, force)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_js(addon: str, action_name: str, tag: str) -> str:
    return f'''/** @odoo-module **/

import {{ Component }} from "@odoo/owl";
import {{ registry }} from "@web/core/registry";

export class {action_name} extends Component {{
    static template = "{addon}.{action_name}";
}}

registry.category("actions").add("{tag}", {action_name});
'''


def build_xml(addon: str, action_name: str, css_class: str) -> str:
    return f'''<?xml version="1.0" encoding="UTF-8" ?>
<templates xml:space="preserve">
    <t t-name="{addon}.{action_name}">
        <div class="{css_class}">
            <h1>{action_name}</h1>
            <p>Replace this template with the real client action UI.</p>
        </div>
    </t>
</templates>
'''


def build_scss(css_class: str) -> str:
    return f'''.{css_class} {{
    padding: 1rem;
}}
'''


def build_action_record(xml_id: str, display_name: str, tag: str) -> str:
    return f'''<record id="{xml_id}" model="ir.actions.client">
    <field name="name">{display_name}</field>
    <field name="tag">{tag}</field>
</record>'''


def asset_snippet(addon: str, rel_dir: str, stem: str, include_scss: bool) -> str:
    lines = [
        '"web.assets_backend": [',
        f'    "{addon}/{rel_dir}/{stem}.js",',
        f'    "{addon}/{rel_dir}/{stem}.xml",',
    ]
    if include_scss:
        lines.append(f'    "{addon}/{rel_dir}/{stem}.scss",')
    lines.append("],")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scaffold an Odoo client action.")
    parser.add_argument("--root", required=True, help="Path to the addon root")
    parser.add_argument("--addon", required=True, help="Addon technical name")
    parser.add_argument("--action-name", required=True, help="Client action class name")
    parser.add_argument("--tag", help="Registry and ir.actions.client tag")
    parser.add_argument("--with-scss", action="store_true", help="Create an SCSS file")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    addon_root = Path(args.root).resolve()
    if not addon_root.exists():
        print(f"Addon root does not exist: {addon_root}", file=sys.stderr)
        return 1

    stem = to_snake_case(args.action_name)
    rel_dir = f"static/src/client_actions/{stem}".replace("\\", "/")
    target_dir = addon_root / Path(rel_dir)
    tag = args.tag or f"{args.addon}.{args.action_name}"
    css_class = f"o_{args.addon}_{stem}_client_action"
    xml_id = f"action_{stem}"

    files = {
        target_dir / f"{stem}.js": build_js(args.addon, args.action_name, tag),
        target_dir / f"{stem}.xml": build_xml(args.addon, args.action_name, css_class),
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
    print(asset_snippet(args.addon, rel_dir, stem, args.with_scss))
    print("\nData XML snippet:")
    print(build_action_record(xml_id, titleize(args.action_name), tag))
    print("\nReminders:")
    print("- Add the data XML file to the manifest.")
    print("- Keep the registry tag stable once menus or actions depend on it.")
    print("- Prefer registries and services before patching framework code.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
