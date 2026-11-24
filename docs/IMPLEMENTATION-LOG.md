# Review implementation log

## RPC boundary and permissions

- Reproduced malformed checkout payloads with the actual Python parser and an
  import-only Odoo adapter: five failures and five errors before the fix.
- Validate list/object shape, 1,000-line bound, positive IDs, boolean quantities
  and float overflow; retain translated messages and positive-demand semantics.
- Execute the settings action as the manager without sudo; add cashier denial.
- Passed local Python boundary tests, static checks, translations and 15 Node tests.

## Environment

- No local Odoo, PostgreSQL, Docker, crapper, dryer or mutator executable found.
- Resolved official Odoo 20 revision for reproducible acceptance CI.
- Preserve the pre-existing untracked `.agents/` directory. No cleanup target
  was identified as safe and necessary. No push is authorized.
