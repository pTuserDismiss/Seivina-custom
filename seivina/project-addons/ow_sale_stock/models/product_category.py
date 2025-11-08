from odoo import models, fields


class ProductCategory(models.Model):
    _inherit = 'product.category'

    carrier_id = fields.Many2one(
        'delivery.carrier',
        string='Default Delivery Method',
        company_dependent=True,
    )
