# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Oakworks: Online Payment',
    'summary': 'Oakworks: Online Payment',
    'version': '18.0.1.0',
    'category': 'Accounting/Accounting',
    'website': 'https://novobi.com',
    'author': 'Novobi, LLC',
    'license': 'OPL-1',
    'depends': [
        # Odoo addons
        'website',
        'sale',
        'payment',
        'account_payment',

        # Novobi addons
        'sale_partner_deposit',

        # Customized addons
        'ow_base',
    ],
    'excludes': [],
    'data': [
        # ============================== DATA =================================

        # ============================== SECURITY =============================

        # ============================== VIEWS ================================

        # ============================== REPORT ===============================

        # ============================== WIZARDS ==============================
    ],
    'assets': {},
    'demo': [],
    'installable': True,
    'application': False,
}
