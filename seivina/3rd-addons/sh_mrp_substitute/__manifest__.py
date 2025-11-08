# -*- coding: utf-8 -*-
# Part of Softhealer Technologies. See LICENSE file for full copyright and licensing details.

{
    "name": "Manufacturing Product Substitute",

    "author": "Softhealer Technologies",

    "website": "https://www.softhealer.com",

    "category": "Manufacturing",

    "license": "OPL-1",

    "version": "0.0.1",

    "support": "support@softhealer.com",

    "summary": "Manufacturing Product Substitutes Manufacturing Substitutes Product Substitutes Products Substitute Add substitute in components Replace substitute in component Add substitute in Bom's components Enable substitute feature Disable substitute feature MRP Product Substitutes MRP Substitutes Product substitution Sustainable manufacturing Sustainable product Product substitution options MRP Product substitution options manufacturing  Product substitution options Sustainable product Sustainable manufacturing product Sustainable MRP product BOM component substitute Bill of material component substitute Manufacturing order Product Substitutes Odoo",

    "description": """In manufacturing, a product substitute refers to a product that can be used as an alternative to another product for a given application or use case. The substitute product usually has similar or comparable features, functions, and performance characteristics as the original product but may have some differences in design, materials, cost, or availability. Components' substitutes can also be defined. It is easy to add or replace substitutes in a manufacturing component's line.""",

    "depends" : ['mrp'],

    "data": [
        'security/sh_res_groups.xml',
        'security/ir.model.access.csv',
        'views/sh_mrp_bom_view.xml',
        'views/sh_mrp_production_view.xml',
        'wizard/sh_add_substitute_wizard_view.xml',

    ],
    'qweb': [
    ],

    "images": ["static/description/background.png", ],

    "auto_install": False,

    "installable": True,

    "application" : True,

    "price": 30,
    
    "currency": "EUR"
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: