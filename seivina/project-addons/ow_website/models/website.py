# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _


class Website(models.Model):
    _inherit = 'website'

    quote_checkout = fields.Boolean(
        string='Quote Checkout',
    )
    disable_checkout = fields.Boolean(
        string='Disable Checkout',
    )

    def _get_checkout_step_list(self):
        self.ensure_one()
        res = super()._get_checkout_step_list()
        if self.quote_checkout:
            for step in res:
                if step[0][0] == 'website_sale.cart':
                    step[1]['main_button'] = 'Continue'
                if step[0][0] == 'website_sale.payment':
                    step[1]['name'] = _("Final Review")
        return res
