# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, fields, models


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'
    
    sh_substitute_product_ids = fields.Many2many('product.product', string='Substitute')
    sh_substitute_product_qty = fields.Float(string='Substitute Qty')


class MrpProduction(models.Model):
    _inherit = ['mrp.production']
    
    def action_add_substitute(self):
        return {
            'name': _('Substitute Product'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sh.add.substitute.wizard',
            'context': {'production_id': self.id},
            'target': 'new',
        }


class ProductProduct(models.Model):
    _inherit = "product.product"
    
    def _compute_used_in_bom_count(self):
        for product in self:
            product.used_in_bom_count = self.env['mrp.bom'].search_count(
                ['|', ('bom_line_ids.product_id', '=', product.id), 
                ('bom_line_ids.sh_substitute_product_ids', 'in', product.id)]
            )

    def action_used_in_bom(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("mrp.mrp_bom_form_action")
        action['domain'] = [
            '|', ('bom_line_ids.product_id', '=', self.id), 
            ('bom_line_ids.sh_substitute_product_ids', 'in', self.id)
        ]
        return action
