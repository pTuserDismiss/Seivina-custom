from collections import Counter
from functools import partial

from odoo import _, api, fields, models
from odoo.osv import expression


class WebsiteSnippetFilter(models.Model):
    _inherit = 'website.snippet.filter'

    def _get_products_optional(self, website, limit, domain, product_template_id=None, **kwargs):
        # This method retrieves products based on the provided domain and optional product template.
        # It is based on function _get_products_%s of OOTB and 'optional' is added to the name.
        products = self.env['product.product']
        current_template = self.env['product.template'].browse(
            product_template_id and int(product_template_id)
        ).exists()
        if current_template:
            included_products = current_template._get_website_optional_product()
            if products := included_products:
                domain = expression.AND([
                    domain,
                    [('id', 'in', products.ids)],
                ])
                products = self.env['product.product'].with_context(
                    display_default_code=False,
                ).search(domain, limit=limit)
        return products
