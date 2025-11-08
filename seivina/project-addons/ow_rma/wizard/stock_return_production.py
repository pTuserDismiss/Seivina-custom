# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, Command, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_round


class StockReturnProductionLine(models.TransientModel):
    _name = 'stock.return.production.line'
    _inherit = 'stock.return.picking.line'
    _rec_name = 'product_id'
    _description = 'Return Manufacturing Line'

    # Override
    wizard_id = fields.Many2one(comodel_name='stock.return.production', string='Wizard')
    move_quantity = fields.Float(related='move_id.product_uom_qty', string="Move Quantity")

    def _prepare_move_default_values(self, return_picking):
        # Override
        vals = {
            'name': return_picking.name,
            'product_id': self.product_id.id,
            'product_uom_qty': self.quantity,
            'product_uom': self.product_id.uom_id.id,
            'picking_id': return_picking.id,
            'state': 'draft',
            'date': fields.Datetime.now(),
            'location_id': return_picking.location_id.id or self.move_id.location_dest_id.id,
            'location_dest_id': return_picking.location_dest_id.id or self.move_id.location_id.id,
            'location_final_id': False,
            'picking_type_id': return_picking.picking_type_id.id,
            'warehouse_id': return_picking.picking_type_id.warehouse_id.id,
            'origin_returned_move_id': self.move_id.id,
            'procure_method': 'make_to_stock',
            'group_id': self.wizard_id.production_id.procurement_group_id.id,
            'raw_material_production_id': False,    # Not shown in MO's component list
        }
        if return_picking.picking_type_id.code == 'outgoing':
            vals['partner_id'] = return_picking.partner_id.id
        return vals

    def _process_line(self, new_picking):
        self.ensure_one()
        if not float_is_zero(self.quantity, precision_rounding=self.uom_id.rounding):
            vals = self._prepare_move_default_values(new_picking)

            if self.move_id:
                self.move_id.copy(vals)
            else:
                self.env['stock.move'].create(vals)
            return True


class StockReturnProduction(models.TransientModel):
    _name = 'stock.return.production'
    _inherit = 'stock.return.picking'
    _description = 'Return Manufacturing'

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if self.env.context.get('active_id') and self.env.context.get('active_model') == 'mrp.production':
            if len(self.env.context.get('active_ids', [])) > 1:
                raise UserError(_('You may only return one manufacturing order at a time.'))
            production = self.env['mrp.production'].browse(self.env.context.get('active_id'))
            if production.exists():
                res.update({'production_id': production.id})
        return res
    
    production_id = fields.Many2one(comodel_name='mrp.production', string='Manufacturing Order')
    product_return_moves = fields.One2many(
        comodel_name='stock.return.production.line',
        inverse_name='wizard_id',
        string='Moves',
        compute='_compute_moves_locations',
        precompute=True,
        readonly=False,
        store=True
    )
    company_id = fields.Many2one(related='production_id.company_id', string='Company')

    @api.depends('production_id')
    def _compute_moves_locations(self):
        # Override
        for wizard in self:
            product_return_moves = [Command.clear()]
            line_fields = list(self.env['stock.return.production.line']._fields)
            product_return_moves_data_tmpl = self.env['stock.return.production.line'].default_get(line_fields)

            for move in wizard.production_id.move_raw_ids.filtered(lambda m: m.state != 'cancel' and not m.scrapped):
                product_return_moves_data = dict(product_return_moves_data_tmpl)
                product_return_moves_data.update(wizard._prepare_stock_return_picking_line_vals_from_move(move))
                product_return_moves.append(Command.create(product_return_moves_data))

            if wizard.production_id and not product_return_moves:
                raise UserError(_("No products to return (only lines in Done state and not fully returned yet can be returned)."))
            if wizard.production_id:
                wizard.product_return_moves = product_return_moves


    def _prepare_picking_default_values(self):
        # Override
        return self._prepare_picking_default_values_based_on(self.production_id)

    def _prepare_src_location_id(self):
        # If Manufacturing Order has been done  -> WH/Production
        # Otherwise                             -> WH/Stock
        warehouse_id = self.production_id.warehouse_id or self.env.ref('stock.warehouse0')
        if self.production_id.state == 'done':
            return self.env['stock.location'].search([
                ('usage', '=', 'production'),
                ('warehouse_id', 'in', [False, warehouse_id.id])
            ], limit=1)
        return warehouse_id.lot_stock_id

    def _prepare_picking_default_values_based_on(self, production):
        # Override
        return_type = self.env.ref('ow_rma.picking_type_vendor_rma')
        location = self._prepare_src_location_id()
        location_dest_id = return_type.default_location_dest_id

        return {
            'move_ids': [],
            'picking_type_id': return_type.id,
            'state': 'draft',
            'production_return_id': production.id,
            'origin': _("Return of %(production_name)s", production_name=production.name),
            'location_id': location.id,
            'location_dest_id': location_dest_id.id,
        }

    def _prepare_exchange_picking(self, return_picking):
        self.ensure_one()
        return_picking.ensure_one()
        return_type = return_picking.picking_type_id

        return return_picking.copy({
            'move_ids': [],
            'picking_type_id': return_type.return_picking_type_id.id,
            'state': 'draft',
            'origin': _("Return of %(picking_name)s", picking_name=return_picking.name),
            'location_id': return_picking.location_dest_id.id,
            'location_dest_id': return_picking.location_id.id,
            'user_id': False,
        })

    def _create_return(self):
        # Override
        for return_move in self.product_return_moves.move_id:
            return_move.move_dest_ids.filtered(lambda m: m.state not in ('done', 'cancel'))._do_unreserve()

        # create new picking for returned products
        # new_picking = self.picking_id.copy(self._prepare_picking_default_values())
        new_picking = self.env['stock.picking'].create(self._prepare_picking_default_values())
        new_picking.user_id = False
        new_picking.message_post_with_source(
            'mail.message_origin_link',
            render_values={'self': new_picking, 'origin': self.production_id},
            subtype_xmlid='mail.mt_note',
        )
        returned_lines = False
        for return_line in self.product_return_moves:
            if return_line._process_line(new_picking):
                returned_lines = True
        if not returned_lines:
            raise UserError(_("Please specify at least one non-zero quantity."))

        new_picking.action_confirm()
        new_picking.action_assign()
        return new_picking

    def _create_exchange(self, return_picking):
        # Create a new picking for exchanged products
        exchange_picking = self._prepare_exchange_picking(return_picking)
        exchange_picking.message_post_with_source(
            'mail.message_origin_link',
            render_values={'self': exchange_picking, 'origin': return_picking},
            subtype_xmlid='mail.mt_note',
        )
        for return_line in self.product_return_moves:
            return_line._process_line(exchange_picking)

        exchange_picking.action_confirm()
        exchange_picking.action_assign()
        return exchange_picking

    def action_create_returns_all(self):
        # Override
        self.ensure_one()
        for return_move in self.product_return_moves:
            stock_move = return_move.move_id
            if not stock_move or stock_move.state == 'cancel' or stock_move.scrapped:
                continue
            quantity = stock_move.product_uom_qty
            for move in stock_move.move_dest_ids:
                if not move.origin_returned_move_id or move.origin_returned_move_id != stock_move:
                    continue
                quantity -= move.product_uom_qty
            product_uom_qty = float_round(quantity, precision_rounding=stock_move.product_id.uom_id.rounding)
            return_move.quantity = product_uom_qty
        return self.action_create_returns()

    def action_create_exchanges(self):
        # Override
        """ Create a return for the active picking, then create a return of
        the return for the exchange picking and open it."""
        action = self.action_create_returns()

        return_picking = self.env['stock.picking'].browse([action['res_id']])
        exchange_picking = self._create_exchange(return_picking)
        # Set the exchange as a return of the return
        exchange_picking.return_id = return_picking
        return action

    def _get_proc_values(self, line):
        self.ensure_one()
        src_location = self._prepare_src_location_id()
        return {
            'group_id': self.production_id.procurement_group_id,
            'date_planned': line.move_id.date or fields.Datetime.now(),
            'warehouse_id': self.production_id.warehouse_id,
            'partner_id': False,
            'location_final_id': line.move_id.location_final_id or src_location,
            'company_id': self.production_id.company_id,
        }
