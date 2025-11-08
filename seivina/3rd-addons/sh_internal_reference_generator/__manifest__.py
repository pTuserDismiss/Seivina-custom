# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Product Internal Reference Generator",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Productivity",
    "license": "OPL-1",
    "summary": "Auo Internal Reference Generator Make Internal Reference Default Module Auto Generate Product Name Auto Generate Reference Number Generate Sequence Reference No Create Category Wise Reference No Custom Internal Reference No Auto Generate Internal Reference Number Auto Generate Internal Reference No Automatic Generate Internal Reference Number Automatic Generate Internal Reference No Odoo customize product internal reference number customize internal reference no customize internal reference number custom internal reference no custom internal reference number Auto internal reference Automatic internal reference Internal Reference Generation Reference Code Generator Internal ID Generator Automated Reference Number Internal Reference Management Unique Reference Generator Reference Number Automation Internal Reference System Odoo",
    "description": """Currently, in odoo there is no way to generate automatically internal reference with customization. Our this module will provide that feature, where you can create a pattern for internal reference of product. You can create or customize internal reference using the product name, sequence, category, attribute with separators. Also, you can set auto-generate internal references while creating a new product.
 Internal Reference Generator Odoo
 By Default Make Internal Reference Module, Auto Generate New Product Reference Number By Name, Automatic Generate Sequence Wise Reference No, Auto Create Category Wise Reference No, Custom Internal Reference No With Attributes Generator Odoo.
  Make Internal Reference Default Module, Auto Generate Product Name Reference Number, Generate Sequence Reference No, Create Category Wise Reference No, Custom Internal Reference No App, Reference No Attributes Generator Odoo.
""",
    "version": "0.0.1",
    "depends": [
        "sale_management",
        "account",
        "product"
    ],
    "data": [
        "security/sh_internal_reference_security_groups.xml",
        "security/ir.model.access.csv",
        "views/res_config_setting_views.xml",
        "wizard/sh_internal_reference_wizard_views.xml",
    ],
    "images": ["static/description/background.png", ],
    "application": True,
    "installable": True,
    "currency": "EUR",
    "price": "15"
}
