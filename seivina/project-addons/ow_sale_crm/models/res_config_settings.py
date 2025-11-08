# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    generate_opportunity = fields.Boolean(
        related='website_id.generate_opportunity',
        readonly=False,
    )
