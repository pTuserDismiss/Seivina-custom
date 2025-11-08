# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class StockMove(models.Model):
    _inherit = 'repair.order'

    feedback_name = fields.Char(
        string='Name',
        tracking=True,
        placeholder='Name of the person talked to',
    )
    feedback_date = fields.Date(
        string='Date',
        tracking=True,
    )
    feedback_note = fields.Text(
        string='Feedback',
        tracking=True,
    )
    feedback_attachment_ids = fields.Many2many(
        'ir.attachment',
        string='Attachments/Images',
    )
