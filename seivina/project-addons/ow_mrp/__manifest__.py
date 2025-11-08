# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Oakworks: Manufacturing',
    'summary': "Includes customizations related to Oakworks' manufacturing processes",
    'version': '18.0.1.0',
    'category': 'Manufacturing',
    'website': 'https://novobi.com',
    'author': 'Novobi, LLC',
    'license': 'OPL-1',
    'depends': [
        # Odoo addons
        'mrp',
        'repair',

        # 3rd-party addons
        'mrp_bom_attribute_match',

        # Customized addons
        'ow_base',
    ],
    'excludes': [],
    'data': [
        # ============================== DATA =================================

        # ============================== SECURITY =============================
        'security/mrp_security.xml',
        'security/ir.model.access.csv',

        # ============================== VIEWS ================================
        'views/mrp_bom_views.xml',
        'views/mrp_production_views.xml',

        # ============================== REPORT ===============================
        'report/mrp_production_templates.xml',
        'report/mrp_report_views_main.xml',
        'report/stock_report_views.xml',

        # ============================== WIZARD ===============================
        'wizard/mrp_add_substitute_wizard.xml',
    ],
    'assets': {},
    'demo': [],
    'installable': True,
    'application': False,
}
