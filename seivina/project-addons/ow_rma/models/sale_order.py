# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SalesOrder(models.Model):
    _inherit = 'sale.order'

    rma_picking_id = fields.Many2one(comodel_name='stock.picking', string='RMA Transfer')
