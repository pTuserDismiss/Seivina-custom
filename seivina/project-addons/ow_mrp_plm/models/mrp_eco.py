from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MrpEco(models.Model):
    _inherit = 'mrp.eco'

    show_qt9_banner = fields.Boolean(
        string="Show QT9 Banner",
        default=True,
    )

    def action_confirm_qt9_reupload(self):
        for eco in self:
            eco.message_post(body=_("Re-upload to QT9 confirmed."))
            eco.show_qt9_banner = False

    def action_new_revision(self):
        """
        Override to create a blank BOM for the product if there's no BOM input
        """
        for eco in self.filtered(
                lambda e: e.type == 'bom' and not e.bom_id and not e.product_tmpl_id.bom_ids
        ):
            new_blank_bom = self.env['mrp.bom'].sudo().create({
                'product_tmpl_id': eco.product_tmpl_id.id,
                'product_uom_id': eco.product_tmpl_id.uom_id.id,
                'product_qty': 1.0,
                'version': 0,
            })
            eco.bom_id = new_blank_bom
        return super().action_new_revision()

    def _get_difference_bom_lines(self, old_bom, new_bom):
        """
        Override to get the difference in Component Template
        """
        new_bom_commands = super()._get_difference_bom_lines(old_bom, new_bom)
        for command in new_bom_commands:
            if len(command) == 3 and isinstance(command[2], dict) and not command[2].get('product_id'):
                command[2]['component_product_tmpl_id'] = self.env['mrp.bom.line'].browse(
                    command[2].get('bom_line_id', 0)
                ).component_template_id.id
        return new_bom_commands

    def open_new_bom(self):
        result = super().open_new_bom()
        result['view_id'] = self.env.ref('ow_mrp_plm.mrp_bom_form_view_ow_mrp_plm').id
        return result


class MrpEcoBomChange(models.Model):
    _inherit = 'mrp.eco.bom.change'

    product_id = fields.Many2one(required=False, string="Component")
    component_product_tmpl_id = fields.Many2one('product.template', string="Component Template")

    @api.constrains('product_id', 'component_product_tmpl_id')
    def _check_product_value(self):
        for eco in self:
            if not eco.product_id and not eco.component_product_tmpl_id:
                raise ValidationError(_('Missing Component and Component Template in BoM changes'))
