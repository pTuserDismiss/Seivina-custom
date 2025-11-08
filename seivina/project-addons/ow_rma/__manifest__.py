# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Oakworks: RMA',
    'summary': 'Oakworks: Return Merchandise Authorization',
    'version': '18.0.1.0',
    'category': 'Inventory/Inventory',
    'website': 'https://novobi.com',
    'author': 'Novobi, LLC',
    'license': 'OPL-1',
    'depends': [
        # Odoo addons
        'account',
        'sale',
        'stock',
        'repair',
        'mrp',
        'quality',
        'quality_control',

        # Customized addons
        'ow_base',
        'ow_quality',
    ],
    'excludes': [],
    'data': [
        # ============================== DATA =================================
        'data/ir_sequence_data.xml',
        'data/stock_location_data.xml',
        'data/stock_picking_type_data.xml',
        'data/quality_point_data.xml',
        'data/mail_template_data.xml',

        # ============================== SECURITY =============================
        'security/ir.model.access.csv',

        # ============================== VIEWS ================================
        'views/stock_picking_type_views.xml',
        'views/stock_picking_views.xml',
        'views/repair_order_views.xml',
        'views/mrp_production_views.xml',

        'views/rma_menus.xml',

        # ============================== REPORT ===============================

        # ============================== WIZARDS ==============================
        'wizard/stock_return_production_views.xml',
    ],
    'assets': {},
    'demo': [],
    'installable': True,
    'application': False,
}
