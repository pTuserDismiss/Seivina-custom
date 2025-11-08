# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    total_quote_quantity_threshold = fields.Float(
        string='Total Quote Qty Greater Than',
        digits='Product Unit of Measure',
    )
    probability_threshold = fields.Float(
        string='Probability Greater Than',
    )
