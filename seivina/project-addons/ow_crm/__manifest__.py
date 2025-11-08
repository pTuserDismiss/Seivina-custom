# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Oakworks: CRM',
    'summary': "Includes customizations related to Oakworks' CRM processes",
    'version': '18.0.1.0',
    'category': 'Sales/CRM',
    'website': 'https://novobi.com',
    'author': 'Novobi, LLC',
    'license': 'OPL-1',
    'depends': [
        'crm',
        'portal',
        'ow_base',
        'ow_approval',
    ],
    'excludes': [],
    'data': [
        # ============================== DATA =================================
        'data/mail_template_data.xml',

        # ============================== SECURITY =============================

        # ============================== VIEWS ================================
        'views/crm_lead_views.xml',
        'views/res_config_settings_views.xml',
        'views/res_partner_form.xml',
        # ============================== REPORT ===============================

        # ============================== WIZARD ===============================

    ],
    'assets': {},
    'demo': [],
    'installable': True,
    'application': False,
}
