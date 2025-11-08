# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    all_move_raw_ids = fields.One2many(
        comodel_name='stock.move',
        inverse_name='production_id',
        compute='_compute_all_move_raw_ids',
        string='All Raw Moves'
    )

    all_workorder_ids = fields.One2many(
        comodel_name='mrp.workorder',
        inverse_name='production_id',
        compute='_compute_all_workorder_ids',
        string='All Work Orders'
    )

    all_quality_check_ids = fields.One2many(
        comodel_name='quality.check',
        inverse_name='production_id',
        compute='_compute_all_quality_check_ids',
        string='All Quality Checks'
    )

    linked_repair_order_ids = fields.One2many(
        comodel_name='repair.order',
        compute='_compute_linked_repair_orders',
        string='Linked Repair Orders'    
    )

    ready_to_mark_done = fields.Boolean(
        compute='_compute_ready_to_mark_done',
        string='Ready to Mark Done',
        store=True,
    )

    @api.depends('state', 'show_produce_all', 'check_ids.quality_state')
    def _compute_ready_to_mark_done(self):
        productions_to_mark_done = self.filtered(lambda p: not p.state in ('done', 'cancel') and p.show_produce_all and all(c.quality_state == 'pass' for c in p.check_ids))
        productions_to_mark_done.ready_to_mark_done = True
        (self - productions_to_mark_done).ready_to_mark_done = False
    
    @api.depends('move_raw_ids.move_line_ids.lot_id')
    def _compute_linked_repair_orders(self):
        for production in self:
            lot_ids = production.move_raw_ids.mapped('move_line_ids.lot_id.id')
            if lot_ids:
                repair_orders = self.env['repair.order'].search([
                    ('lot_id', 'in', lot_ids)
                ])
                production.linked_repair_order_ids = repair_orders
            else:
                production.linked_repair_order_ids = False

    @api.depends('move_raw_ids')
    def _compute_all_move_raw_ids(self):
        for mo in self:
            mo.all_move_raw_ids = mo.get_all_move_raw_recursive()

    @api.depends('workorder_ids')
    def _compute_all_workorder_ids(self):
        for mo in self:
            mo.all_workorder_ids = mo.get_all_workorder_recursive()

    @api.depends('check_ids')
    def _compute_all_quality_check_ids(self):
        for mo in self:
            mo.all_quality_check_ids = mo.get_all_quality_check_recursive()

    # -------------------------------------------------------------------------
    # ACTIONS
    # -------------------------------------------------------------------------
    
    def action_confirm(self):
        res = super().action_confirm()
        self._replace_unavailable_components()
        return res

    def button_mark_done(self):
        if self._check_components_unavailable():
            raise UserError(_('Cannot close the MOs. Some MOs are on hold due to insufficient components.'))
        
        return super().button_mark_done()

    def action_substitute(self):
        self.ensure_one()
        substitue_wizard = self.env['mrp.add.substitute.wizard'].create({
            'production_id': self.id,
        })
        return substitue_wizard._get_records_action(
            name=_('Substitute Product'),
            target='new'
        )

    # -------------------------------------------------------------------------
    # CRUD
    # -------------------------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        for val in vals_list:
            if val.get('bom_id'):
                bom = self.env['mrp.bom'].browse(val['bom_id'])
                product = self.env['product.product'].browse(val['product_id'])
                bom._create_component_dynamic_variant(manufacturing_product_ptavs=product.product_template_variant_value_ids)
        return super().create(vals_list)

    def write(self, vals):
        date_start = vals.get('date_start')
        result = super().write(vals)

        if date_start:
            for production in self:
                orders = production._get_orders()
                if not orders:
                    continue
                
                production_new_date = production.date_finished
                if not production_new_date:
                    continue

                for order in orders:
                    order_delivery_date = order.commitment_date or order.expected_date

                    if order_delivery_date and production_new_date > order_delivery_date:
                        order.write({'commitment_date': production_new_date})
        return result

    # -------------------------------------------------------------------------
    # HELPERS
    # -------------------------------------------------------------------------

    def _check_components_unavailable(self):
        return self.filtered(lambda production: production.components_availability_state == 'unavailable')

    def _get_orders(self):
        return self.procurement_group_id.mrp_production_ids.move_dest_ids.group_id.sale_id + self.sale_line_id.order_id
    
    def _calculate_substitute_quantity(self, move, substitute, record):
        """
        Calculate substitute quantity.
        
        :param move: stock.move record
        :param substitute: mrp.bom.line.substitute record
        :param record: mrp.production record
        """
        bom_uom = move.bom_line_id.bom_id.product_uom_id
        production_uom = record.product_uom_id
        
        fg_bom_qty = bom_uom._compute_quantity(move.bom_line_id.bom_id.product_qty, production_uom)
        fg_production_qty = record.product_uom_qty
        substitute_qty = substitute.product_uom_qty / fg_bom_qty * fg_production_qty
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        return float_round(substitute_qty, precision_digits=precision)
    
    def _replace_unavailable_components(self):
        invalid_productions = self.filtered(lambda r: r.state not in ('draft', 'confirmed', 'progress'))
        if invalid_productions:
            raise UserError(_('Substitute components can only be changed for Manufacturing Orders that are in progress.'))

        for record in self:
            for move in record.move_raw_ids:
                component_uom = move.product_id.uom_id
                component_qty = move.product_uom._compute_quantity(move.product_uom_qty, component_uom)
                component_available_qty = move.product_id.qty_available
                if (
                    not move.bom_line_id
                    or move.is_substitute
                    or float_compare(component_qty, component_available_qty, precision_rounding=component_uom.rounding) < 0
                ):
                    continue

                substitutes = move.bom_line_id.substitute_ids.sorted('sequence')
                
                for substitute in substitutes:
                    substitute_qty = self._calculate_substitute_quantity(move, substitute, record)
                    
                    if substitute.product_id and not substitute._is_available(required_qty=substitute_qty):
                        continue
                    
                    if substitute.product_template_id:
                        compatible_variants = substitute.get_compatible_variants(move.product_id)
                        substitute_product = False
                        
                        for variant in compatible_variants:
                            if substitute._is_available(variant, required_qty=substitute_qty):
                                substitute_product = variant
                                break
                        
                        if not substitute_product:
                            continue
                        
                        move_vals = substitute._prepare_subtitute_stock_move_vals(
                            product_id=substitute_product.id,
                            bom_line_id=move.bom_line_id.id,
                            raw_material_production_id=record.id,
                            product_uom_qty=substitute_qty,
                        )
                        move.write(move_vals)
                        break

                    elif substitute.product_id:
                        move_vals = substitute._prepare_subtitute_stock_move_vals(
                            product_id=substitute.product_id.id,
                            bom_line_id=move.bom_line_id.id,
                            raw_material_production_id=record.id,
                            product_uom_qty=substitute_qty,
                        )
                        move.write(move_vals)
                        break
    
    def get_all_move_raw_recursive(self):
        """Return all raw material stock.move records for this MO and its sub-MOs."""
        self.ensure_one()
        all_moves = self.env['stock.move']

        def _collect_moves(mo_rec):
            nonlocal all_moves
            all_moves |= mo_rec.move_raw_ids
            sub_mos = self.search([('origin', '=', mo_rec.name)])
            for sub_mo in sub_mos:
                _collect_moves(sub_mo)

        _collect_moves(self)
        return all_moves
    
    def get_all_workorder_recursive(self):
        self.ensure_one()
        all_workorders = self.env['mrp.workorder']

        def _collect_workorders(mo_rec):
            nonlocal all_workorders
            all_workorders |= mo_rec.workorder_ids
            sub_mos = self.search([('origin', '=', mo_rec.name)])
            for sub_mo in sub_mos:
                _collect_workorders(sub_mo)

        _collect_workorders(self)
        return all_workorders
    
    def get_all_quality_check_recursive(self):
        self.ensure_one()
        all_quality_checks = self.env['quality.check']

        def _collect_quality_checks(mo_rec):
            nonlocal all_quality_checks
            all_quality_checks |= mo_rec.check_ids
            sub_mos = self.search([('origin', '=', mo_rec.name)])
            for sub_mo in sub_mos:
                _collect_quality_checks(sub_mo)

        _collect_quality_checks(self)
        return all_quality_checks
    
    def action_report_device_history_records(self):
        completed_mos = self.filtered(lambda mo: mo.state == 'done')
        if not completed_mos:
            raise UserError("You must select at least one completed Manufacturing Order to print the report.")
        return self.env.ref('ow_mrp.action_report_device_history_records').report_action(completed_mos)
    