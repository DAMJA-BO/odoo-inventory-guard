# Odoo skill selection

When writing or reviewing Odoo addon code, load the relevant available skills before starting the change or review. Do not wait for an explicit slash command.

- `odoo-guidelines`: addon code outside `static/`, including manifests, Python and ORM, XML views and data, and server-side tests.
- `odoo-web-guidelines`: JavaScript, Owl templates, SCSS, and frontend tests under an addon's `static/` directory.
- `odoo-security`: defensive reviews and changes involving access controls, company isolation, public methods or RPC, controller authentication, `sudo()`, or raw SQL.

Load only the skills relevant to the task. Combine them when the change crosses those boundaries; skip them when none applies.
