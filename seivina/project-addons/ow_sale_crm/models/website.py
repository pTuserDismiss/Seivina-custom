# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, _


class Website(models.Model):
    _inherit = 'website'

    generate_opportunity = fields.Boolean(
        string='Auto generate CRM opportunities for unpaid orders',
    )
