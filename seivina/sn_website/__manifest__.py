# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Seivina: Website',
    'summary': 'Seivina: Website',
    'version': '18.0.1.0',
    'category': 'Website',
    'author': 'Seivina, LLC',
    'license': '',
    'depends': [
        # Odoo addons
        'website_sale',
    ],
    'excludes': [],
    'data': [
        # ============================== DATA =================================

        # ============================== SECURITY =============================

        # ============================== VIEWS ================================
        'views/website_template.xml',

        # ============================== REPORT ===============================

        # ============================== WIZARDS ==============================
    ],
    'assets': {},
    'demo': [],
    'installable': True,
    'application': False,
}
