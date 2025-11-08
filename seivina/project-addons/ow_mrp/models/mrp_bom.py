# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    def explode(self, product, quantity, picking_type=False, never_attribute_values=False):
        self._create_component_dynamic_variant(manufacturing_product_ptavs=product.product_template_variant_value_ids)
        return super().explode(product, quantity, picking_type, never_attribute_values)

    def _create_component_dynamic_variant(self, manufacturing_product_ptavs=False):
        """
        Creates all component dynamic variants under the current BOM with attribute values matching manufacturing_product_ptavs

        :param manufacturing_product_ptavs: product.template.attribute.value recordset of the manufacturing product
        """
        related_dynamic_combinations = self.env['product.template.attribute.value'].search([
            ('product_tmpl_id', 'in', (self.bom_line_ids.component_template_id | self.product_tmpl_id).ids),
            ('attribute_id.create_variant', '=', 'dynamic'),
        ])
        for bom in self:
            for bom_line in bom.bom_line_ids.filtered(lambda l: l.match_on_attribute_ids):
                match_attribute_ids = bom_line.match_on_attribute_ids
                if all(attribute.create_variant != 'dynamic' for attribute in match_attribute_ids):
                    continue
                dynamic_combinations = related_dynamic_combinations.filtered(lambda c: c.attribute_id in match_attribute_ids)
                all_component_dynamic_combinations = dynamic_combinations.filtered(
                    lambda c: c.product_tmpl_id == bom_line.component_template_id
                )
                if manufacturing_product_ptavs:
                    matching_values = manufacturing_product_ptavs.filtered(
                        lambda c: c.attribute_id in match_attribute_ids
                    ).product_attribute_value_id
                    all_component_dynamic_combinations = all_component_dynamic_combinations.filtered(
                        lambda c: c.product_attribute_value_id.id in matching_values.ids
                    )
                    combination = bom_line.component_template_id._get_closest_possible_combination(all_component_dynamic_combinations)
                    bom_line.component_template_id._create_product_variant(combination)
                else:
                    manufacturing_product_ptavs = dynamic_combinations.filtered(
                        lambda c: c.product_tmpl_id == bom_line.bom_id.product_tmpl_id
                    )
                    for combination in all_component_dynamic_combinations:
                        if combination.product_attribute_value_id in manufacturing_product_ptavs.product_attribute_value_id:
                            combination = bom_line.component_template_id._get_closest_possible_combination(combination)
                            bom_line.component_template_id._create_product_variant(combination)

    @api.onchange('operation_ids')
    def _onchange_operation_ids(self):
        records = self.filtered(lambda r: r.operation_ids.filtered(lambda o: o.time_cycle_manual <= 0))
        if records:
            raise ValidationError(_("The Default Duration must be greater than 0."))
