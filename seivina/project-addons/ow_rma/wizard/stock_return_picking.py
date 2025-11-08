# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import models, Command


class StockReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    def _prepare_picking_default_values(self):
        picking_vals = super()._prepare_picking_default_values()
        if self._context.get('rma_customer_return'):
            picking_vals['origin'] = f'Return to Customer of {self.picking_id.name}'
        return picking_vals


class ReturnPickingLine(models.TransientModel):
    _inherit = 'stock.return.picking.line'

    def _prepare_move_default_values(self, new_picking):
        move_vals = super()._prepare_move_default_values(new_picking)

        # When a return order is created from a delivery order, auto populate the expected lot/serial numbers
        # from its original stock.move.line
        if self.move_id.has_tracking != 'none' and self.move_id.picking_id.picking_type_code == 'outgoing':
            expected_lots = self.move_id.move_line_ids.lot_id
            if expected_lots:
                move_vals['expected_lot_ids'] = [Command.set(expected_lots.ids)]

        return move_vals
