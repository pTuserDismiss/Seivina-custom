# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Oakworks: Website',
    'summary': "Includes customizations related to Oakworks' website processes",
    'version': '18.0.1.0',
    'category': 'Website/Website',
    'website': 'https://novobi.com',
    'author': 'Novobi, LLC',
    'license': 'OPL-1',
    'depends': [
        'website_sale',
        'website_sale_comparison',
        'payment_custom',
        'ow_base',
        'ow_sale_crm',
    ],
    'excludes': [],
    'data': [
        # ============================== DATA =================================
        'data/ir_model_fields.xml',
        'data/website_data.xml',
        'data/mail_template_data.xml',
        # ============================== SECURITY =============================

        # ============================== VIEWS ================================
        'views/res_config_settings_views.xml',
        'views/website_template.xml',
        'views/product_views.xml',
        'views/sale_order_views.xml',

        # ============================== REPORT ===============================

        # ============================== WIZARD ===============================

    ],
    'assets': {
        'web.assets_frontend': [
            'ow_website/static/src/js/request_quote.js',
            'ow_website/static/src/css/request_quote.css',
        ],
    },
    'demo': [],
    'installable': True,
    'application': False,
}
