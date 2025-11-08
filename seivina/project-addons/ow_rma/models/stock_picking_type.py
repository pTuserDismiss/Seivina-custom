# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    is_return = fields.Boolean(string='Is Return Operation?', default=False)
    show_return_actions = fields.Boolean(string='Show Return Action Buttons')

    def _try_loading_rma(self):
        # Customer Return
        delivery_op = self.env.ref('stock.picking_type_out', raise_if_not_found=False)
        rma_op = self.env.ref('ow_rma.picking_type_rma', raise_if_not_found=False)
        if delivery_op and rma_op:
            delivery_op.return_picking_type_id = rma_op

        # Vendor Return
        receipt_op = self.env.ref('stock.picking_type_in', raise_if_not_found=False)
        quality_op = self.search([('name', 'ilike', 'Quality Control')], limit=1)
        vendor_rma_op = self.env.ref('ow_rma.picking_type_vendor_rma', raise_if_not_found=False)
        if receipt_op and vendor_rma_op:
            receipt_op.return_picking_type_id = vendor_rma_op
        if quality_op and vendor_rma_op:
            quality_op.return_picking_type_id = vendor_rma_op
            vendor_rma_op.default_location_src_id = quality_op.default_location_dest_id
