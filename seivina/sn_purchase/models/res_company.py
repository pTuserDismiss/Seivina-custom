# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    purchase_attachment_ids = fields.Many2many(
        comodel_name='ir.attachment',
        string='Default Terms & Conditions'
    )
