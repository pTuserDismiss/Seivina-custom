# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.tools import float_compare
from odoo.exceptions import ValidationError


class MrpBomLineSubstitute(models.Model):
    _name = 'mrp.bom.line.substitute'
    _description = 'BoM Line Substitute'
    _order = 'sequence, id'
    _rec_name = 'display_name'

    def _get_default_product_uom_id(self):
        return self.env['uom.uom'].search([], limit=1, order='id').id

    sequence = fields.Integer(string='Priority', default=10)
    bom_line_id = fields.Many2one(
        comodel_name='mrp.bom.line',
        string='BoM Line',
        required=True,
        ondelete='cascade'
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        ondelete='restrict'
    )
    product_template_id = fields.Many2one(
        comodel_name='product.template',
        string='Product Template',
        ondelete='restrict'
    )
    product_uom_category_id = fields.Many2one(
        "uom.category",
        compute="_compute_product_uom_category_id",
    )
    product_uom_id = fields.Many2one(
        comodel_name='uom.uom',
        string='Product Unit of Measure',
        default=_get_default_product_uom_id,
        required=True,
        domain="[('category_id', '=', product_uom_category_id)]"
    )
    product_uom_qty = fields.Float(
        string='Substitute Quantity',
        digits='Product Unit of Measure',
        default=1.0,
        required=True
    )
    bom_line_component_template_id = fields.Many2one('product.template', related='bom_line_id.component_template_id')
    bom_id = fields.Many2one(related='bom_line_id.bom_id')

    @api.constrains('product_template_id', 'bom_line_id')
    def _check_substitute_template_attributes(self):
        for rec in self:
            if not rec.product_template_id or not rec.bom_line_id.component_template_id:
                continue
            comp_attrs = (
                rec.product_template_id.valid_product_template_attribute_line_ids.attribute_id
            )
            prod_attrs = (
                rec.bom_line_id.component_template_id.valid_product_template_attribute_line_ids.attribute_id
            )
            if not comp_attrs:
                raise ValidationError(
                    _(
                        "No match on attribute has been detected for Substitute "
                        "(Product Template) %s",
                        rec.product_template_id.display_name,
                    )
                )
            if not all(attr in prod_attrs for attr in comp_attrs):
                raise ValidationError(
                    _(
                        "Some attributes of the substitute product template are not included in the "
                        "component template attributes."
                    )
                )

    @api.depends('product_id', 'product_template_id')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = rec.product_id.partner_ref or rec.product_template_id.name

    @api.depends("product_template_id", "product_id")
    def _compute_product_uom_category_id(self):
        for rec in self:
            rec.product_uom_category_id = rec.product_id.uom_id.category_id or rec.product_template_id.uom_id.category_id

    def _is_available(self, variant=None, required_qty=None):
        """
        Check if this substitute is fully available to replace the original component
        """
        self.ensure_one()
        product_uom = self.product_template_id.uom_id or self.product_id.uom_id
        
        if required_qty is not None:
            product_qty = required_qty
        else:
            product_qty = self.product_uom_id._compute_quantity(self.product_uom_qty, product_uom)
            
        if self.product_template_id:
            if not variant:
                return False
            product_available_qty = variant.free_qty
        else:
            product_available_qty = self.product_id.free_qty
        return float_compare(product_qty, product_available_qty, precision_rounding=product_uom.rounding) <= 0

    def _prepare_subtitute_stock_move_vals(self, product_id, **kwargs):
        self.ensure_one()
        product = self.env['product.product'].browse(product_id)
        product_uom_qty = kwargs.get('product_uom_qty', self.product_uom_qty)
        return {
            'product_id': product.id,
            'name': product.name,
            'product_uom': self.product_uom_id.id,
            'product_uom_qty': product_uom_qty,
            'state': 'confirmed',
            'is_substitute': True,
            **kwargs,
        }

    def get_compatible_variants(self, selected_product):
        self.ensure_one()
        if not self.product_template_id:
            return self.env['product.product']
        
        selected_attr_values = selected_product.product_template_variant_value_ids.product_attribute_value_id
        substitute_variants = self.product_template_id.product_variant_ids.filtered(lambda p: p.active)
        
        compatible_variants = substitute_variants.filtered(lambda variant:
            all(attr in variant.product_template_variant_value_ids.product_attribute_value_id for attr in selected_attr_values)
        )
        
        return compatible_variants
