from odoo import api, fields, models, _


class ProductProduct(models.Model):
    _inherit = "product.product"
    
    is_long_lead_time_product = fields.Boolean(string='Long Lead Time Product',
                                               compute='_compute_is_long_lead_time_product',
                                               search='_search_is_long_lead_time_product')
    gtin = fields.Char(string='GTIN')

    @api.onchange('inspection_label')
    def _onchange_inspection_label(self):
        self.product_tmpl_id._onchange_inspection_label()

    @api.depends('product_tmpl_id.product_tag_ids')
    def _compute_is_long_lead_time_product(self):
        long_lead_time_tag = self.env.ref('ow_product.long_lead_time_tag', raise_if_not_found=False)
        if not long_lead_time_tag:
            self.is_long_lead_time_product = False
            return
        for product in self:
            product.is_long_lead_time_product = long_lead_time_tag.id in product.product_tag_ids.ids

    def _search_is_long_lead_time_product(self, operator, value):
        if operator not in ['=', '!=']:
            raise ValueError(_('This operator is not supported'))
        if not isinstance(value, bool):
            raise ValueError(_('Value should be True or False (not %s)'), value)

        long_lead_time_tag = self.env.ref('ow_product.long_lead_time_tag', raise_if_not_found=False)
        if not long_lead_time_tag:
            if (operator == '!=' and value) or (operator == '=' and not value):
                return [('active', '=', True)]
            else:
                return [('id', '=', -1)]
        else:
            long_lead_time_products = self.env['product.product'].search([
                ('active', '=', True), ('company_id', 'in', [False, self.env.company.id])
            ]).filtered(lambda p: long_lead_time_tag.id in p.product_tag_ids.ids)
            if (operator == '!=' and value) or (operator == '=' and not value):
                domain_operator = 'not in'
            else:
                domain_operator = 'in'
            return [('id', domain_operator, long_lead_time_products.ids)]
