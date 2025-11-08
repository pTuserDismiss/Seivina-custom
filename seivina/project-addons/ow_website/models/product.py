from odoo import api, models, fields
from odoo.osv import expression


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    ecommerce_specifications = fields.Html(string="Ecommerce Specifications")

    def _get_website_optional_product(self):
        domain = self.env['website'].sale_product_domain()
        if not self.env.user._is_internal():
            domain = expression.AND([domain, [('is_published', '=', True)]])
        return self.optional_product_ids.product_variant_id.filtered_domain(domain)

    @api.model
    def _get_optional_product_filter_id(self):
        return self.env.ref('ow_website.dynamic_filter_cross_selling_optional_products').id
