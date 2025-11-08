from odoo import models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _get_default_carrier(self):
        return self.categ_id.carrier_id or self.env['delivery.carrier']


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _get_default_carrier(self):
        return self.categ_id.carrier_id or self.product_tmpl_id._get_default_carrier()
