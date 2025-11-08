# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Novobi: Vendor Deposit',
    'summary': 'Novobi: Vendor Deposit',
    'version': '18.0.1.0',
    'category': 'Accounting',
    'website': 'https://novobi.com',
    'author': 'Novobi, LLC',
    'license': 'OPL-1',
    'depends': [
        # Odoo addons
        'purchase',

        # Customized addons
        'account_partner_deposit',
    ],
    'excludes': [],
    'data': [
        # ============================== DATA =================================

        # ============================== SECURITY =============================

        # ============================== VIEWS ================================
        'views/account_payment_views.xml',
        'views/purchase_order_views.xml',

        # ============================== REPORT ===============================

        # ============================== WIZARDS ==============================
    ],
    'assets': {},
    'demo': [],
    'installable': True,
    'application': False,
}
