# -*- coding: utf-8 -*-
from odoo import models,fields

class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    taxjar_category_id = fields.Many2one("taxjar.category",string="TaxJar Category",help="For specific product.")
