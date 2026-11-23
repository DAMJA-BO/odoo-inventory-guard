{
    "name": "Odoo Inventory Guard",
    "summary": "Company-aware protection against negative physical stock",
    "version": "20.0.1.0.0",
    "category": "Inventory/Inventory",
    "author": "Ronald Torrez",
    "website": "https://github.com/ronaldtorrez/odoo-inventory-guard",
    "license": "Other OSI approved licence",
    "depends": ["stock"],
    "data": ["security/policy_security.xml", "security/ir.access.csv", "views/policy_views.xml"],
    "application": True,
    "installable": True,
}
