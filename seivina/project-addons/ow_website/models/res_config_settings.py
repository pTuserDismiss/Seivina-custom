# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    quote_checkout = fields.Boolean(
        related='website_id.quote_checkout',
        string='Quote Checkout',
        readonly=False,
    )

    disable_checkout = fields.Boolean(
        related='website_id.disable_checkout',
        string='Disable Checkout',
        readonly=False,
    )
