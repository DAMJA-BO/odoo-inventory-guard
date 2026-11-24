// SPDX-License-Identifier: Apache-2.0
import js from "@eslint/js";
import globals from "globals";

export default [
    { ignores: ["node_modules/", ".claude/", ".agents/"] },
    js.configs.recommended,
    {
        files: ["pos_inventory_guard/static/**/*.js"],
        languageOptions: { sourceType: "module", globals: globals.browser },
    },
    {
        files: ["tests/**/*.mjs", "eslint.config.js"],
        languageOptions: { sourceType: "module", globals: globals.node },
    },
];
