#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Dependency-free syntax and packaging checks; does not replace Odoo tests."""

import ast
from pathlib import Path
import xml.etree.ElementTree as ET


def main():
    root = Path(__file__).resolve().parents[1]
    for path in root.rglob("*.py"):
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for path in root.rglob("*.xml"):
        ET.parse(path)
    for manifest_path in root.glob("*/__manifest__.py"):
        addon = manifest_path.parent
        manifest = ast.literal_eval(manifest_path.read_text(encoding="utf-8"))
        assert manifest["version"].startswith("20.0."), "Expected Odoo 20 version"
        assert manifest["license"] == "Other OSI approved licence"
        for relative in manifest["data"]:
            assert (addon / relative).is_file(), relative
        for paths in manifest.get("assets", {}).values():
            for relative in paths:
                assert (root / relative).is_file(), relative
        if addon.name == "inventory_guard":
            assert "security/ir.access.csv" in manifest["data"]
            assert not (addon / "security" / "ir.model.access.csv").exists()
            assert 'model="ir.rule"' not in "\n".join(
                path.read_text(encoding="utf-8") for path in addon.rglob("*.xml")
            )
    for name in ("LICENSE", "NOTICE", "README.md", "CONTRIBUTING.md"):
        assert (root / name).is_file(), name
    assert "Apache License" in (root / "LICENSE").read_text(encoding="utf-8")
    print("Python syntax, XML, manifest and license packaging checks passed.")


if __name__ == "__main__":
    main()
