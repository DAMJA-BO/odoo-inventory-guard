{
    "name": "Odoo POS Stock Guard",
    "summary": "Prevent POS checkout when available stock is insufficient",
    "version": "20.0.1.0.2",
    "category": "Sales/Point of Sale",
    "author": "Ronald Torrez",
    "website": "https://github.com/ronaldtorrez/odoo-pos-stock-guard",
    "license": "Other OSI approved licence",
    "depends": ["pos_stock"],
    "data": ["views/pos_config_views.xml"],
    "assets": {
        "point_of_sale._assets_pos": [
            "pos_stock_guard/static/src/app/payment_screen_patch.js",
        ],
    },
    "installable": True,
    "application": False,
}
