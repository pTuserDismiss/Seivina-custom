# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    purchase_attachment_ids = fields.Many2many(
        related='company_id.purchase_attachment_ids',
        string='Default Terms & Conditions',
        readonly=False
    )
