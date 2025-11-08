# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _, Command
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    picking_type_return = fields.Boolean(related='picking_type_id.is_return', string='Is Return Picking?')
    show_return_actions = fields.Boolean(string='Show Return Action Buttons', related='picking_type_id.show_return_actions')

    move_refund_ids = fields.One2many(comodel_name='account.move', inverse_name='rma_picking_id', string='Refunds')
    move_refund_count = fields.Integer(string='Refund Count', compute='_compute_move_refund_count')

    sale_replacement_ids = fields.One2many(comodel_name='sale.order', inverse_name='rma_picking_id', string='Replacements')
    sale_replacement_count = fields.Integer(string='Replacement Count', compute='_compute_sale_replacement_count')

    production_return_id = fields.Many2one(comodel_name='mrp.production', string='Manufacturing Order')

    def _default_picking_type_id(self):
        # Override to search for default Operation Type, which could be Return Operation or not.
        picking_type_code = self.env.context.get('restricted_picking_type_code')
        picking_type_return = self.env.context.get('restricted_picking_type_return')

        if picking_type_code:
            picking_types = self.env['stock.picking.type'].search([
                ('code', '=', picking_type_code),
                ('company_id', '=', self.env.company.id),
                ('picking_type_return', '=', picking_type_return),
            ])
            return picking_types[:1].id

    # -------------------------------------------------------------------------
    # COMPUTE METHODS
    # -------------------------------------------------------------------------

    @api.depends('move_refund_ids')
    def _compute_move_refund_count(self):
        for record in self:
            record.move_refund_count = len(record.move_refund_ids)

    @api.depends('sale_replacement_ids')
    def _compute_sale_replacement_count(self):
        for record in self:
            record.sale_replacement_count = len(record.sale_replacement_ids)

    # -------------------------------------------------------------------------
    # ACTIONS
    # -------------------------------------------------------------------------

    def button_validate(self):
        self._check_valid_rma_lots()
        return super().button_validate()

    @api.model
    def get_action_picking_tree_rma(self):
        return self._get_action('ow_rma.action_picking_tree_rma')

    @api.model
    def get_action_picking_tree_vendor_rma(self):
        return self._get_action('ow_rma.action_picking_tree_vendor_rma')

    def _get_next_transfers(self):
        next_pickings = super()._get_next_transfers()
        return next_pickings.filtered(lambda p: p != self.return_id)

    def action_rma_refund(self):
        self.ensure_one()
        refund_vals = self._prepare_rma_refund_vals()
        refund = self.env['account.move'].create(refund_vals)
        return self.action_view_rma_refund(refund)

    def action_rma_replacement(self):
        self.ensure_one()
        sale_replacement_vals = self._prepare_rma_sale_replacement_vals()
        if self.sale_id:
            sale_replacement = self.sale_id.copy(default=sale_replacement_vals)
        else:
            sale_replacement_vals['partner_id'] = self.partner_id.id
            sale_replacement = self.env['sale.order'].create(sale_replacement_vals)
        return self.action_view_rma_replacement(sale_replacement)

    def action_rma_repair(self):
        self.ensure_one()
        repair_vals_list = self._prepare_rma_repair_vals_list()
        self.env['repair.order'].create(repair_vals_list)
        return self.action_view_repairs()

    def action_rma_customer_return(self):
        self.ensure_one()
        # Create the wizard and return full quantity on all return lines
        return_wizard = self.with_context(
            active_model='stock.picking',
            active_id=self.id,
            rma_customer_return=True,
        ).env['stock.return.picking'].create({})
        return return_wizard.action_create_returns_all()

    def action_rma_scrap(self):
        return self.button_scrap()

    def action_view_rma_refund(self, refund=None):
        return (refund or self.move_refund_ids)._get_records_action(name=_('Refund'))

    def action_view_rma_replacement(self, sale_replacement=None):
        return (sale_replacement or self.sale_replacement_ids)._get_records_action(name=_('Replacement'))

    def action_report_mismatch(self):
        self.ensure_one()
        template = self.env.ref('ow_rma.email_template_report_mismatch', raise_if_not_found=False)
        if not template:
            return
        email_to = template.email_to or ''
        if self.sale_id.user_id.partner_id.email:
            if email_to:
                email_to += ','
            email_to += self.sale_id.user_id.partner_id.email
        compose_ctx = dict(
            default_composition_mode='comment',
            default_model='stock.picking',
            default_template_id=template.id,
            default_email_layout_xmlid='ow_rma.mail_transfer_layout_ow',
            default_email_to=email_to,
        )
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mail.compose.message',
            'view_mode': 'form',
            'view_id': False,
            'target': 'new',
            'context': compose_ctx,
        }

    # -------------------------------------------------------------------------
    # HELPER METHODS
    # -------------------------------------------------------------------------

    def _get_mismatch_move_lines(self):
        return self.move_ids_without_package.filtered(lambda m: m.move_line_ids.lot_id - m.expected_lot_ids)

    def get_formview_url(self):
        self.ensure_one()
        return f'/odoo/deliveries/{str(self.id)}/?view_type=form'

    def _check_valid_rma_lots(self):
        for record in self.filtered(lambda r: r.state not in ('done', 'cancel')):
            for move in record.move_ids_without_package.filtered('expected_lot_ids'):
                expected_lots = move.expected_lot_ids
                actual_lots = move.move_line_ids.lot_id
                if actual_lots - expected_lots:
                    raise UserError(_('Lot/Serial numbers do not match with the expected. Please check and try again.'))

    def _prepare_rma_product_lines_vals(self):
        self.ensure_one()
        val_list = []
        for move_line in self.move_line_ids.filtered(lambda r: r.state == 'done'):
            product = move_line.product_id
            sale_line = move_line.move_id.sale_line_id

            # Conver stock.move UoM, qty, unit price to SO line's units
            if sale_line:
                uom = sale_line.product_uom
                qty_done = move_line.product_uom_id._compute_quantity(move_line.qty_done, sale_line.product_uom, rounding_method='HALF-UP')
                price_unit = sale_line.price_unit
                taxes = sale_line.tax_id
            # If SO line is not found, convert stock.move UoM, qty, unit price to Product's units
            else:
                uom = move_line.product_uom_id
                qty_done = move_line.qty_done
                price_unit = product.uom_id._compute_price(product.lst_price, move_line.product_uom_id)
                taxes = product.taxes_id

            val_list.append({
                'product_id': product.id,
                'product_uom_id': uom.id,
                'price_unit': price_unit,
                'quantity': qty_done,
                'tax_ids': [Command.set(taxes.ids)],
                'sale_line_ids': [Command.set(sale_line.ids)],
            })
        return val_list

    def _prepare_rma_refund_vals(self):
        self.ensure_one()
        rma_number = self.name
        val_list = self._prepare_rma_product_lines_vals()
        refund_lines = [Command.create(product_line_val) for product_line_val in val_list]

        return  {
            'move_type': 'out_refund',
            'ref': f'Refund for: {rma_number}',
            'invoice_origin': rma_number,
            'partner_id': self.sale_id.partner_invoice_id.id or self.partner_id.id,
            'invoice_line_ids': refund_lines,
            'rma_picking_id': self.id,
        }

    def _prepare_rma_sale_replacement_vals(self):
        self.ensure_one()
        val_list = self._prepare_rma_product_lines_vals()
        order_lines = [Command.create({
            'product_id': product_line_val['product_id'],
            'product_uom_qty': product_line_val['quantity'],
            'product_uom': product_line_val['product_uom_id'],
            'price_unit': product_line_val['price_unit'],
            'tax_id': product_line_val['tax_ids'],
        }) for product_line_val in val_list]

        return {
            'client_order_ref': f'Replacement for: {self.name}',
            'order_line': order_lines,
            'rma_picking_id': self.id,
        }

    def _prepare_rma_repair_vals_list(self):
        self.ensure_one()
        partner = self.sale_id.partner_id or self.partner_id
        src_location = self.location_dest_id

        return [{
            'partner_id': partner.id,
            'picking_id': self.id,
            'picking_type_id': src_location.warehouse_id.repair_type_id.id,
            'product_location_src_id': src_location.id,     # RMA Location
            'product_location_dest_id': src_location.id,    # RMA Location, instead of WH/Stock
            'product_id': move_line.product_id.id,
            'lot_id': move_line.lot_id.id,
            'product_qty': move_line.qty_done,
            'product_uom': move_line.product_uom_id.id,
        } for move_line in self.move_line_ids.filtered(lambda r: r.state == 'done')]
    