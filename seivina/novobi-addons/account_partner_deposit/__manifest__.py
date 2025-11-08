# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Novobi: Account Deposit',
    'summary': 'Novobi: Account Deposit',
    'version': '18.0.1.0',
    'category': 'Accounting',
    'website': 'https://novobi.com',
    'author': 'Novobi, LLC',
    'license': 'OPL-1',
    'depends': [
        # Odoo addons
        'account',
        'account_reports',
        'account_followup',
    ],
    'excludes': [],
    'data': [
        # ============================== DATA =================================
        'data/coa_chart_data.xml',

        # ============================== SECURITY =============================
        'security/ir.model.access.csv',

        # ============================== VIEWS ================================
        'views/res_partner_views.xml',
        'views/account_move_views.xml',
        'views/account_payment_views.xml',

        # ============================== REPORT ===============================
        # 'report/account_followup_report_templates.xml',

        # ============================== WIZARDS ==============================
        'wizard/order_make_deposit_views.xml'
    ],
    'assets': {},
    'demo': [],
    'installable': True,
    'application': False,
}
