# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    expected_lot_ids = fields.Many2many(
        comodel_name='stock.lot',
        string='Expected Lot/Serial Numbers',
        domain="[('product_id', '=', product_id)]",
        tracking=True
    )
