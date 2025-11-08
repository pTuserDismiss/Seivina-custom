# -*- coding: utf-8 -*-
{
    'name': "Customer Number Generator",

    'summary': """
    The Customer Number Module for Odoo automatically generates unique customer numbers for customers
        """,

    'description': """
       Contact, Customer Number
    """,

    'author': "W4 Services AG",
    'website': "https://just-odoo.agency",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Administration',
    'currency': 'EUR',
    'version': '18.0.1.1.2',
    'license': 'OPL-1',
    # any module necessary for this one to work correctly
    'depends': ['base','contacts'],

    # always loaded
    'data': [
        'data/data.xml',
        'views/views.xml',
        'views/settings.xml'

    ],
    'images': ['static/description/cover.gif'],
}
