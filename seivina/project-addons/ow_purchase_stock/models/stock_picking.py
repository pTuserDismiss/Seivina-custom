# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # Override to switch from related to compute field, which allows manual modifications
    purchase_id = fields.Many2one(related=False, compute='_compute_purchase_id', store=True, readonly=False, tracking=True)

    @api.depends('move_ids.purchase_line_id')
    def _compute_purchase_id(self):
        for record in self:
            record.purchase_id = record.move_ids.purchase_line_id.order_id
