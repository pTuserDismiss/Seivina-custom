# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    substitute_ids = fields.One2many(
        comodel_name='mrp.bom.line.substitute',
        inverse_name='bom_line_id',
        string='Substitutes',
        copy=True
    )
    component_template_id = fields.Many2one(ondelete='cascade')
    product_id = fields.Many2one(ondelete='cascade')

    @api.constrains('product_id', 'component_template_id')
    def _check_bom_attribute_compatibility(self):
        bom_lines = self.filtered(lambda r: not (r.product_id or r.component_template_id))
        if bom_lines:
            raise ValidationError(_('Component or Component Template is missing!'))

    @api.depends('product_id', 'component_template_id')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = rec.product_id.name or rec.component_template_id.name

    @api.constrains('component_template_id', 'bom_id')
    def _check_component_template_attributes(self):
        """
        Validate that when component has the same attribute as finished good,
        all values of that attribute in finished good must exist in component
        """
        self.check_component_template_attributes()

    @api.onchange('component_template_id')
    def _onchange_component_template_id(self):
        """
        Onchange handler for component_template_id to validate attributes and attribute values
        """
        self.check_component_template_attributes()

    def check_component_template_attributes(self):
        for rec in self:
            if not rec.component_template_id or not rec.bom_id.product_tmpl_id:
                return
            
            bom_attr_lines = rec.bom_id.product_tmpl_id.valid_product_template_attribute_line_ids
            bom_attributes = bom_attr_lines.attribute_id
            
            comp_attr_lines = rec.component_template_id.valid_product_template_attribute_line_ids
            component_attributes = comp_attr_lines.attribute_id
            
            common_attributes = bom_attributes & component_attributes
            
            warning_messages = []
            
            for attribute in common_attributes:
                bom_attribute_line = bom_attr_lines.filtered(lambda x: x.attribute_id == attribute)
                bom_values = bom_attribute_line.product_template_value_ids.product_attribute_value_id
                
                comp_attribute_line = comp_attr_lines.filtered(lambda x: x.attribute_id == attribute)
                comp_values = comp_attribute_line.product_template_value_ids.product_attribute_value_id
                
                missing_values = bom_values - comp_values
                
                if missing_values:
                    warning_messages.append(_(
                        'Attribute "%(attr)s": missing values %(missing_values)s',
                        attr=attribute.name,
                        missing_values=', '.join(missing_values.mapped('name'))
                    ))

            if warning_messages:
                raise ValidationError(_(
                    'Component template "%(component)s" should have attribute values that match those of the '
                    'finished goods for the same attributes.',
                    component=rec.component_template_id.name,
                ))

    def action_view_substitutes(self):
        self.ensure_one()
        if not self.product_id and not self.component_template_id:
            raise UserError(_('No component selected!'))

        return self._get_records_action(
            name=_('Define Substitutes'),
            target='new',
            context={
                'form_view_ref': 'ow_mrp.view_mrp_bom_line_form_ow_mrp_substitute',
            }
        )
