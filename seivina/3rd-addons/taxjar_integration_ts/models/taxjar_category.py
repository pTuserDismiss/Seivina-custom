from odoo import fields,api,models
from odoo.osv import expression

class TaxjarCategory(models.Model):
    _name = 'taxjar.category'
    _order = 'name'
    _description = 'TaxJar Category'

    name = fields.Char('Name',required=True)
    product_tax_code = fields.Char('Tax Code')
    description = fields.Char('Description')
    account_id = fields.Many2one('taxjar.account',string='TaxJar Account')

    @api.depends('name', 'product_tax_code')
    def _compute_display_name(self):
        for category in self:
            category.display_name = category.product_tax_code and f'[{category.product_tax_code}] {category.name}' or category.name

    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        domain = domain or []
        if operator == 'ilike':
            domain = expression.AND([['|', ('product_tax_code', 'ilike', name), ('name', operator, name)], domain])
        return self._search(domain, limit=limit, order=order)