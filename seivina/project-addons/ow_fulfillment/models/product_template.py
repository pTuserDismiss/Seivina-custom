# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_length = fields.Float(
        string='Product Length',
        digits='Volume'
    )
    product_width = fields.Float(
        string='Product Width', 
        digits='Volume'
    )
    product_height = fields.Float(
        string='Product Height',
        digits='Volume'
    )
    volume = fields.Float(
        compute='_compute_product_volume',
        store=True,
        readonly=True,
    )

    shipping_length = fields.Float(
        string='Shipping Length',
        digits='Volume'
    )
    shipping_width = fields.Float(
        string='Shipping Width',
        digits='Volume'
    )
    shipping_height = fields.Float(
        string='Shipping Height',
        digits='Volume'
    )
    shipping_volume = fields.Float(
        string='Shipping Volume',
        compute='_compute_shipping_volume',
        store=True,
        digits='Volume'
    )

    @api.depends('product_length', 'product_width', 'product_height')
    def _compute_product_volume(self):
        for product in self:
            if product.product_length and product.product_width and product.product_height:
                product.volume = product.product_length * product.product_width * product.product_height
            else:
                product.volume = 0.0

    @api.depends('shipping_length', 'shipping_width', 'shipping_height')
    def _compute_shipping_volume(self):
        for product in self:
            if product.shipping_length and product.shipping_width and product.shipping_height:
                product.shipping_volume = product.shipping_length * product.shipping_width * product.shipping_height
            else:
                product.shipping_volume = 0.0
