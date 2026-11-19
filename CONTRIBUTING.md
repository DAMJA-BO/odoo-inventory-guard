# Contributing

Contributions, bug reports and documentation improvements are welcome.

## Workflow

1. Explain the problem in an issue, including the exact Odoo version and steps
   to reproduce. Use synthetic data, not customer records or database backups.
2. Create a branch from the supported `20.0` development line (or the default
   branch until the repository is published).
3. Keep a pull request focused on one behavior. Use English names, comments,
   docstrings, commit messages and documentation.
4. Add regression coverage for changed stock rules. Run the local checks and the
   Odoo tests listed in `docs/TESTING.md`. Report checks you could not run.
5. Document changes and limitations in `CHANGELOG.md` and the README as needed.

## Design conventions

Keep model hooks small. Put stock rules in `models/stock_guard.py` and UI feedback
in the payment-screen patch. Retain translatable user-facing strings. Respect
record rules and company access; do not add broad `sudo()` access. Never commit
inside a business method or swallow database serialization errors. Prefer narrow
extension hooks over copying Odoo methods.

## Licensing contributions

By intentionally submitting a contribution for inclusion, you offer it under
Apache License 2.0, subject to section 5 of that license. Submit only work you
have permission to license; identify all third-party material and its license.
You retain copyright in your contribution. No copyright assignment or separate
CLA is required. This does not grant the maintainer unrestricted rights to
relicense your contribution under incompatible terms.

## Review checklist

- No company secrets, personal data or copied Enterprise implementation code.
- Company isolation, duplicate lines, returns and precision remain covered.
- Draft/replayed orders and failed stock transfers retain correct behavior.
- Runtime checks target Odoo 20, not older POS APIs.
