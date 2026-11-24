# Interface translations

Inventory Guard uses English source strings and ships general English (`en.po`) and
Spanish (`es.po`) catalogs under `pos_inventory_guard/i18n/`. There are no regional
catalogs. The English catalog mirrors the source; English also works as the
fallback when a translation is missing. Documentation remains in English.

## Enable a language

Install the desired language in Odoo, select it in the user's preferences and
install or upgrade Inventory Guard so its translations are loaded. Reload the browser
and reopen the POS after changing language or updating catalogs. The language is
the active Odoo user/session language; it is not a separate Inventory Guard setting.
Switching employee profiles within a POS is not a language selector.

Example: in Spanish, Show stock badges becomes Mostrar indicadores de existencias
and Out of stock becomes Sin existencias. Inventory Guard remains the product name.
Product names, company names and location names are business data and follow
Odoo's own data translations; this catalog does not translate them.

## Maintain translations

Keep Python `_()` and JavaScript `_t()` calls around literal source messages.
Use Odoo's translation export for this module to regenerate the POT and merge
new terms into both PO catalogs. Preserve references, the odoo-python and
odoo-javascript markers, interpolation tokens and line breaks. Do not translate
technical field names or JavaScript selection keys.

The `ir.http` extension includes this addon in frontend translation modules,
following the Odoo 20 POS hook. Without it, JavaScript messages can remain in
English even when settings translations are present.

Run `python scripts/check_translations.py` after changing source messages or
catalogs. The check compares the POS catalogs against source terms inventoried by
`translation_terms.py`. For the core, it compares the PO catalogs against the POT;
it does not discover missing core source terms. Regenerate the POT with Odoo or
cross-check new core view text and its references against the template.
Extend the inventory if new translation patterns are introduced.

## Acceptance checks on Odoo.sh

Use a disposable development build with Spanish installed. Verify settings names,
help text, selection labels, toolbar text, stock badges and both early and final
shortage messages in Spanish. Repeat in English. Include dynamic quantities,
location names, tooltips and connection-failure messages. Check the browser console
and server logs for translation or formatting errors.

Local checks verify catalogs, not rendered Odoo screens. Record actual acceptance
results separately in the [testing checklist](TESTING.md).
