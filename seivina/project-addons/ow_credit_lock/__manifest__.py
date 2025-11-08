# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Oakworks: Credit Check Lock',
    'summary': 'Oakworks: Credit Check Lock',
    'version': '18.0.1.0',
    'category': 'Hidden/Tools',
    'website': 'https://novobi.com',
    'author': 'Novobi, LLC',
    'license': 'OPL-1',
    'depends': [
        # Odoo addons
        'mail',
        'stock',
        'sale',
        'sale_stock',
        'mrp',
        'sale_mrp',
        'account',

        # Novobi addons
        'account_partner_deposit',
        'sale_partner_deposit',

        # Customized addons
        'ow_base',
        'ow_approval',
        'ow_mrp',
    ],
    'excludes': [],
    'data': [
        # ============================== DATA =================================

        # ============================== SECURITY =============================
        'security/credit_lock_security.xml',

        # ============================== VIEWS ================================
        'views/sale_order_views.xml',
        'views/mrp_production_views.xml',
        'views/stock_picking_views.xml',
        'views/account_payment_term_views.xml',

        # ============================== REPORT ===============================

        # ============================== WIZARDS ==============================
    ],
    'assets': {},
    'demo': [],
    'installable': True,
    'application': False,
}
