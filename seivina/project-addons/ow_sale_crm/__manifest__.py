# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

{
    "name": "Oakworks: Sales CRM",
    "summary": "Includes customizations related to Oakworks' sale-crm process",
    "version": "18.0.1.0",
    "category": "Hidden",
    "website": "https://novobi.com",
    "author": "Novobi, Inc.",
    "license": "OPL-1",
    "depends": [
        "sale_crm",
        "website_sale",
        "ow_base",
        "ow_sale",
    ],
    "excludes": [],
    "data": [
        # ============================== DATA =================================

        # ============================== REPORT =============================

        # ============================== SECURITY ================================

        # ============================== VIEWS ================================
        "views/res_config_settings_view.xml",
    ],
    "application": False,
    "installable": True,
}
