# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Oakworks: Approval',
    'summary': 'Oakworks: Approval',
    'version': '18.0.1.0',
    'category': 'Hidden/Tools',
    'website': 'https://novobi.com',
    'author': 'Novobi, LLC',
    'license': 'OPL-1',
    'depends': [
        # Odoo addons
        'mail',
        'hr',

        # Customized addons
        'ow_base',
    ],
    'excludes': [],
    'data': [
        # ============================== SECURITY =============================
        'security/ir.model.access.csv',
        
        # ============================== DATA =================================

        # ============================== VIEWS ================================
        'views/approval_log_views.xml',
        'views/hr_employee_views.xml',
        # ============================== REPORT ===============================

        # ============================== WIZARDS ==============================
        'wizard/approval_wizard_views.xml',
    ],
    'assets': {},
    'demo': [],
    'installable': True,
    'application': False,
}
