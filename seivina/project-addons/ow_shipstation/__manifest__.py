# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Oakworks: ShipStation',
    'summary': 'Oakworks: ShipStation Customization',
    'version': '18.0.1.0',
    'category': 'Sales/Delivery',
    'website': 'https://novobi.com',
    'author': 'Novobi, LLC',
    'license': 'OPL-1',
    'images': ['static/description/icon.png'],
    'depends': [
        # Odoo addons
        'delivery',

        # 3rd-party addons
        'shipstation_ept',

        # Customized addons
        'ow_base',
    ],
    'excludes': [],
    'data': [
        # ============================== DATA =================================

        # ============================== SECURITY =============================

        # ============================== VIEWS ================================

        # ============================== REPORT ===============================

        # ============================== WIZARD ===============================
    ],
    'assets': {},
    'demo': [],
    'installable': True,
    'application': False,
}
