# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

{
    "name": "Oakworks: PLM",
    "summary": "Includes customizations related to Oakworks' PLM processes",
    "version": "18.0.1.0",
    "category": "Manufacturing",
    "author": "Novobi, Inc.",
    "license": "OPL-1",
    "website": "https://www.novobi.com",
    "application": False,
    "auto_install": False,
    "installable": True,
    "depends": ["ow_base", "mrp_plm"],
    "data": [
        # ============================== DATA =================================

        # ============================== SECURITY =============================

        # ============================== VIEWS ================================
        "views/mrp_bom_views.xml",
        "views/mrp_eco_views.xml",
        "views/res_config_settings_views.xml",

        # ============================== REPORT ===============================

        # ============================== WIZARD ===============================

        # ============================== MENU =================================
    ],
}
