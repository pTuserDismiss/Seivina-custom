# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Oakworks: Modify 3RD Shipping Integration',
    'summary': "Oakworks: Modify 3RD Shipping Integration",
    'version': '18.0.1.0',
    'category': 'Sales/Delivery',
    'website': 'https://novobi.com',
    'author': 'Novobi, LLC',
    'license': 'OPL-1',
    'images': ['static/description/icon.png'],
    'depends': [
        # Odoo addons
        'delivery',
        'product',

        # 3rd-party addons
        'freightview_delivery_carrier',

        # Customized addons
        'ow_base',
    ],
    'excludes': [],
    'data': [
        # ============================== DATA =================================
        'data/shipstation_carrier_update.xml',

        # ============================== SECURITY =============================

        # ============================== VIEWS ================================
        'views/product_template_views.xml',
        'views/report_deliveryslip.xml',
        
        # ============================== REPORT ===============================

        # ============================== WIZARD ===============================
        'wizard/choose_delivery_carrier_views.xml',
    ],
    'assets': {},
    'demo': [],
    'installable': True,
    'application': False,
}
