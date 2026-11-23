#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check catalog completeness and interpolation tokens without Odoo dependencies."""

import ast
from pathlib import Path
import re

from translation_terms import terms


def read_catalog(path):
    entries = {}
    current = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("msgid "):
            current = ast.literal_eval(line[6:])
        elif line.startswith("msgstr ") and current:
            assert current not in entries, f"Duplicate term: {current}"
            entries[current] = ast.literal_eval(line[7:])
    return entries


def main():
    folder = Path(__file__).resolve().parents[1] / "pos_inventory_guard" / "i18n"
    expected = set(terms())
    tokens = re.compile(r"%\([^)]+\)[sd]|%[sd]")
    for name in ("pos_inventory_guard.pot", "en.po", "es.po"):
        catalog = read_catalog(folder / name)
        assert set(catalog) == expected, f"Catalog coverage mismatch: {name}"
        for source, target in catalog.items():
            if name.endswith(".pot"):
                assert not target
                continue
            assert target.strip(), f"Empty translation in {name}: {source}"
            assert tokens.findall(source) == tokens.findall(target), source
            assert source.count("\n") == target.count("\n"), source
            if name == "en.po":
                assert source == target, source
        print(f"{name}: {len(catalog)} terms checked")


if __name__ == "__main__":
    main()
