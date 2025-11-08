# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

{
    "name": "Oakworks: Sales",
    "summary": "Includes customizations related to Oakworks' sales process",
    "version": "18.0.1.0",
    "category": "Sales/Sales",
    "author": "Novobi, Inc.",
    "license": "OPL-1",
    "website": "https://www.novobi.com",
    "application": False,
    "auto_install": False,
    "installable": True,
    "depends": ["sale"],
    "data": [
        # ============================== DATA =================================

        # ============================== SECURITY =============================

        # ============================== VIEWS ================================
        "views/res_partner_views.xml",
        "views/sale_order_views.xml",

        # ============================== REPORT ===============================

        # ============================== WIZARD ===============================

        # ============================== MENU =================================
    ],
}
