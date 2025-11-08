# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import api, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.onchange('product_length', 'product_width', 'product_height')
    def _compute_product_volume(self):
        for product in self:
            if product.product_length and product.product_width and product.product_height:
                product.volume = product.product_length * product.product_width * product.product_height
            else:
                product.volume = 0.0
