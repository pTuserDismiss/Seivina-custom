# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models, Command
from odoo.exceptions import ValidationError
from odoo.tools import float_round


class MrpAddSubstituteWizard(models.TransientModel):
    _name = 'mrp.add.substitute.wizard'
    _description = 'Add Substitute Wizard'

    production_id = fields.Many2one(
        comodel_name='mrp.production',
        string='Manufacturing Order',
        required=True,
        readonly=True
    )
    available_product_ids = fields.Many2many(
        comodel_name='product.product',
        string='Available Products',
        compute='_compute_available_product_ids'
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        domain="[('id', 'in', available_product_ids)]"
    )
    bom_line_id = fields.Many2one(
        comodel_name='mrp.bom.line',
        string='Bom Line'
    )
    available_variant_ids = fields.Many2many(
        comodel_name='product.product',
        string='Available Variants'
    )
    available_substitute_ids = fields.Many2many(
        comodel_name='mrp.bom.line.substitute',
        string='Available Substitutes'
    )
    substitute_id = fields.Many2one(
        comodel_name='mrp.bom.line.substitute',
        string='Substitute',
        domain="[('id', 'in', available_substitute_ids)]",
    )
    substitute_product_id = fields.Many2one(
        comodel_name='product.product',
        string='Substitute Product',
        domain="[('id', 'in', available_variant_ids)]",
    )
    substitute_product_uom_id = fields.Many2one(
        related='substitute_id.product_uom_id',
    )
    substitute_product_uom_qty = fields.Float(
        related='substitute_id.product_uom_qty',
    )
    operation = fields.Selection(
        selection=[('replace', 'Replace'), ('add', 'Add')],
        default='replace',
        required=True
    )
    substitute_quantity = fields.Float(
        string='Substitute Quantity',
    )

    # -------------------------------------------------------------------------
    # COMPUTE / ONCHANGE METHODS
    # -------------------------------------------------------------------------
    @api.depends('production_id')
    def _compute_available_product_ids(self):
        for record in self:
            available_products = self.env['product.product']
            bom_lines = record.production_id.bom_id.bom_line_ids
            for bom_line in bom_lines:
                if bom_line.product_id:
                    available_products |= bom_line.product_id
                elif bom_line.component_template_id:
                    # based on _check_variants_validity method in mrp_bom_attribute_match
                    component_template = bom_line.component_template_id
                    manufacturing_product = record.production_id.product_id
                    
                    comp_attrs = component_template.valid_product_template_attribute_line_ids.attribute_id
                    prod_attrs = manufacturing_product.valid_product_template_attribute_line_ids.attribute_id
                    
                    if all(attr in prod_attrs for attr in comp_attrs):
                        combination = self.env["product.template.attribute.value"]
                        for ptav in manufacturing_product.product_template_attribute_value_ids:
                            combination |= self.env["product.template.attribute.value"].search([
                                ("product_tmpl_id", "=", component_template.id),
                                ("attribute_id", "=", ptav.attribute_id.id),
                                ("product_attribute_value_id", "=", ptav.product_attribute_value_id.id),
                            ])
                        
                        if combination:
                            compatible_variant = component_template._get_variant_for_combination(combination)
                            if compatible_variant and compatible_variant.active:
                                available_products |= compatible_variant
            
            record.available_product_ids = [Command.set(available_products.ids)]

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if not self.product_id or not self.production_id or not self.production_id.bom_id:
            self.update({
                'bom_line_id': False,
                'available_substitute_ids': [Command.clear()],
                'substitute_id': False,
            })
            return
            
        bom_lines = self.production_id.bom_id.bom_line_ids
        bom_line = bom_lines.filtered(lambda r: r.product_id == self.product_id)
        if not bom_line:
            bom_line = bom_lines.filtered(lambda r: r.component_template_id == self.product_id.product_tmpl_id)
        bom_line = bom_line and bom_line[0]
        
        if not bom_line:
            self.update({
                'bom_line_id': False,
                'available_substitute_ids': [Command.clear()],
                'substitute_id': False,
            })
            return
            
        substitutes = bom_line.substitute_ids.sorted('sequence') 
        substitute = substitutes and substitutes[0] or False

        self.update({
            'bom_line_id': bom_line,
            'available_substitute_ids': [Command.set(substitutes.ids)],
            'substitute_id': substitute,
        })

    @api.onchange('substitute_id')
    def _onchange_substitute_id(self):
        for record in self:
            if record.substitute_id.product_template_id:
                compatible_variants = record.substitute_id.get_compatible_variants(record.product_id)
                record.update({
                    'available_variant_ids': [Command.set(compatible_variants.ids)],
                    'substitute_product_id': compatible_variants[0],
                })
            elif record.substitute_id.product_id:
                record.update({
                    'available_variant_ids': [Command.set([record.substitute_id.product_id.id])],
                    'substitute_product_id': record.substitute_id.product_id,
                })
            record.substitute_quantity = record._calculate_substitute_quantity()

    # -------------------------------------------------------------------------
    # ACTIONS
    # -------------------------------------------------------------------------

    def _calculate_substitute_quantity(self):
        """
        Calculate the substitute quantity based on the current production and substitute
        """
        bom_uom = self.bom_line_id.bom_id.product_uom_id
        production_uom = self.production_id.product_uom_id
        
        fg_bom_qty = bom_uom._compute_quantity(self.bom_line_id.bom_id.product_qty, production_uom)
        fg_production_qty = self.production_id.product_uom_qty
        substitute_qty = self.substitute_id.product_uom_qty / fg_bom_qty * fg_production_qty
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        
        return float_round(substitute_qty, precision_digits=precision)

    def action_add_substitute(self):
        self.ensure_one()
        if not self.substitute_product_id:
            raise ValidationError(_('Please select a substitute product.'))
        
        move_vals = self.substitute_id._prepare_subtitute_stock_move_vals(
            raw_material_production_id=self.production_id.id,
            product_id=self.substitute_product_id.id,
            product_uom_qty=self.substitute_quantity,
        )
        self.env['stock.move'].create(move_vals)

    def action_replace_substitute(self):
        self.ensure_one()
        if not self.substitute_product_id:
            raise ValidationError(_('Please select a substitute product.'))
        
        current_move = self.production_id.move_raw_ids.filtered(
            lambda r: r.bom_line_id == self.bom_line_id
        )
        current_move.write({'state': 'draft'})
        current_move.unlink()
        
        # When replacing a component with a substitute product, consider retaining
        # the link to the original bom_line_id on the new stock.move line.
        move_vals = self.substitute_id._prepare_subtitute_stock_move_vals(
            bom_line_id=self.bom_line_id.id,
            raw_material_production_id=self.production_id.id,
            product_id=self.substitute_product_id.id,
            product_uom_qty=self.substitute_quantity,
        )
        self.env['stock.move'].create(move_vals)
