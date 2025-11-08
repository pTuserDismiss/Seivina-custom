# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Oakworks: Repair',
    'summary': "Includes customizations related to Oakworks' Repair processes",
    'version': '18.0.0.0',
    'category': 'Inventory/Inventory',
    'website': 'https://novobi.com',
    'author': 'Novobi, LLC',
    'license': 'OPL-1',
    'depends': [
        'repair',
        'ow_base',
    ],
    'excludes': [],
    'data': [
        # ============================== DATA =================================

        # ============================== SECURITY =============================

        # ============================== VIEWS ================================
        "views/repair_views.xml",

        # ============================== REPORT ===============================

        # ============================== WIZARD ===============================
    ],
    'assets': {},
    'demo': [],
    'installable': True,
    'application': False,
}
