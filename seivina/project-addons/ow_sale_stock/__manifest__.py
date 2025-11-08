# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

{
    "name": "Oakworks: Sales Stock",
    "summary": "Includes customizations related to Oakworks' sale-stock process",
    "version": "18.0.1.0",
    "category": "Sales/Delivery",
    "website": "https://novobi.com",
    "author": "Novobi, Inc.",
    "license": "OPL-1",
    "depends": [
        # Odoo addons
        "mail",
        "sale_stock",

        # 3rd addons
        "shipstation_ept",

        # Customized addons
        "ow_base",
    ],
    "excludes": [],
    "data": [
        # ============================== DATA =================================

        # ============================== REPORT =============================

        # ============================== SECURITY ================================
        "security/ir.model.access.csv",

        # ============================== VIEWS ================================
        "views/sale_order_views.xml",
        "views/stock_picking_views.xml",
        "views/product_category_views.xml",
        "wizard/shipping_confirmation_wizard_views.xml",
    ],
    "application": False,
    "installable": True,
}
