# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Seivina: Purchase',
    'summary': 'Seivina: Purchase',
    'version': '18.0.1.0',
    'category': 'Purchase',
    'website': 'https://novobi.com',
    'author': 'Novobi, LLC',
    'license': 'OPL-1',
    'depends': [
        # Odoo addons
        'purchase',
    ],
    'excludes': [],
    'data': [
        # ============================== DATA =================================

        # ============================== SECURITY =============================

        # ============================== VIEWS ================================
        # 'views/res_config_settings_views.xml',
        'views/purchase_order_views.xml',
        # 'wizard/mail_compose_message_views.xml',

        # ============================== REPORT ===============================

        # ============================== WIZARDS ==============================
    ],
    'assets': {},
    'demo': [],
    'installable': True,
    'application': False,
}
