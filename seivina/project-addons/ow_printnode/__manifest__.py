# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Oakworks: Printnode',
    'summary': "Includes customizations related to Oakworks' printnode processes",
    'version': '18.0.1.0',
    'category': 'Printnode',
    'website': 'https://novobi.com',
    'author': 'Novobi, LLC',
    'license': 'OPL-1',
    'depends': [
        # Odoo addons

        # 3rd-party addons
        'printnode_base',

        # Customized addons
        'ow_base',
        'ow_product',
    ],
    'excludes': [],
    'data': [
        # ============================== DATA =================================

        # ============================== SECURITY =============================

        # ============================== VIEWS ================================
        "views/res_config_settings.xml",
        "views/stock_picking_views.xml",
        # ============================== REPORT ===============================

        # ============================== WIZARD ===============================
    ],
    'assets': {},
    'demo': [],
    'installable': True,
    'application': False,
}
