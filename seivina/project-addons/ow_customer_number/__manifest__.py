# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Oakworks: Customer Number',
    'summary': "Includes customizations related to w4_customer_number",
    'version': '18.0.1.0',
    'category': 'Administration',
    'website': 'https://novobi.com',
    'author': 'Novobi, LLC',
    'license': 'OPL-1',
    'depends': [
        'w4_customer_number',
        'ow_base',
    ],
    'excludes': [],
    'data': [
        # ============================== DATA =================================

        # ============================== SECURITY =============================

        # ============================== VIEWS ================================
        'views/res_partner_form.xml',
        # ============================== REPORT ===============================

        # ============================== WIZARD ===============================

    ],
    'assets': {},
    'demo': [],
    'installable': True,
    'application': False,
}
