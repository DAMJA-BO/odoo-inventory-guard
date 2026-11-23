#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""List addon translation terms for local coverage checks (not an Odoo exporter)."""

import ast
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ADDON = ROOT / "pos_inventory_guard"


def terms():
    result = {}

    def add(value, reference, javascript=False):
        if value and value.strip() and any(c.isalpha() for c in value):
            item = result.setdefault(value, {"refs": [], "javascript": False})
            if reference not in item["refs"]:
                item["refs"].append(reference)
            item["javascript"] |= javascript

    for path in (ADDON / "models").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        model = "pos_config" if path.stem == "pos_config" else "res_config_settings"
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "_":
                if node.args and isinstance(node.args[0], ast.Constant):
                    add(node.args[0].value, f"code:addons/{path.relative_to(ROOT).as_posix()}:0")
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
                call = node.value
                if not isinstance(call.func, ast.Attribute) or not isinstance(call.func.value, ast.Name) or call.func.value.id != "fields":
                    continue
                name = node.targets[0].id
                ref = f"pos_inventory_guard.field_{model}__{name}"
                for kw in call.keywords:
                    if kw.arg in ("string", "help") and isinstance(kw.value, ast.Constant):
                        kind = "field_description" if kw.arg == "string" else "help"
                        add(kw.value.value, f"model:ir.model.fields,{kind}:{ref}")
                if call.func.attr == "Selection" and call.args:
                    for key, label in ast.literal_eval(call.args[0]):
                        add(label, f"model:ir.model.fields.selection,name:pos_inventory_guard.selection__{model}__{name}__{key}")
    for path in (ADDON / "static").rglob("*.js"):
        for match in re.finditer(r'_t\("((?:[^"\\]|\\.)*)"', path.read_text(encoding="utf-8")):
            add(json.loads('"' + match.group(1) + '"'), f"code:addons/{path.relative_to(ROOT).as_posix()}:0", True)
    # Related settings fields inherit labels/help and selection values, but have
    # their own translation references in the settings model.
    for value, item in list(result.items()):
        for ref in list(item["refs"]):
            if "field_pos_config__" in ref:
                add(value, ref.replace("field_pos_config__", "field_res_config_settings__pos_"))
            elif "selection__pos_config__" in ref:
                add(value, ref.replace("selection__pos_config__", "selection__res_config_settings__pos_"))
    for path in ADDON.rglob("*.xml"):
        tree = ET.parse(path)
        containers = tree.findall(".//record") if "views" in path.parts else [tree.getroot()]
        for container in containers:
            ref = (f"model_terms:ir.ui.view,arch_db:pos_inventory_guard.{container.attrib['id']}"
                   if "views" in path.parts else f"code:addons/{path.relative_to(ROOT).as_posix()}:0")
            for node in container.iter():
                if node.tag in ("record", "field", "xpath", "templates"):
                    continue
                for attr in ("string", "help", "title", "label", "aria-label"):
                    add(node.get(attr), ref, "static" in path.parts)
                add((node.text or "").strip(), ref, "static" in path.parts)
                add((node.tail or "").strip(), ref, "static" in path.parts)
    return result


if __name__ == "__main__":
    print(json.dumps(terms(), ensure_ascii=True))
