# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import models, _
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def action_stock_return_production(self):
        self.ensure_one()
        if self.reservation_state == 'assigned':
            raise UserError(_('You need to unreserve the components before returning them to vendor'))
        
        return self.env['ir.actions.actions']._for_xml_id('ow_rma.action_stock_return_production')
    
    def action_view_mo_delivery(self):
        action = super().action_view_mo_delivery()
        # If Manufacturing Order has been done  -> default source location is WH/Production
        # Otherwise                             -> default source location is WH/Stock
        warehouse_id = self.warehouse_id or self.env.ref('stock.warehouse0')
        src_loc = self.env['stock.location']
        if self.state == 'done':
            src_loc = self.env['stock.location'].search([
                ('usage', '=', 'production'),
                ('warehouse_id', 'in', [False, warehouse_id.id])
            ], limit=1)
        else:
            src_loc = warehouse_id.lot_stock_id
        action['context'].update({
            'search_default_production_return_id': [self.id],
            'default_production_return_id': self.id,
            'default_picking_type_id': self.env.ref('ow_rma.picking_type_vendor_rma').id,
            'default_location_id': src_loc.id
        })
        return action
