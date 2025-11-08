# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Oakworks: Quality',
    'summary': 'Oakworks: Quality',
    'version': '18.0.1.0',
    'category': 'Manufacturing/Quality',
    'website': 'https://novobi.com',
    'author': 'Novobi, LLC',
    'license': 'OPL-1',
    'depends': [
        # Odoo addons
        'quality',
        'quality_control',

        # Customized addons
        'ow_base',
    ],
    'excludes': [],
    'data': [
        # ============================== DATA =================================

        # ============================== SECURITY =============================

        # ============================== VIEWS ================================
        'views/quality_point_views.xml',
        'views/quality_check_views.xml',

        # ============================== REPORT ===============================

        # ============================== WIZARDS ==============================
        'wizard/quality_check_wizard_views.xml',
    ],
    'assets': {},
    'demo': [],
    'installable': True,
    'application': False,
}
