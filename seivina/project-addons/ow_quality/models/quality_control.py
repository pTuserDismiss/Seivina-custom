# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class QualityPoint(models.Model):
    _inherit = 'quality.point'

    measure_frequency_type = fields.Selection(selection_add=[
        ('interval', 'Interval')
    ], ondelete={'interval': 'set default'})
