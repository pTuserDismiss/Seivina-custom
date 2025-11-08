# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class TicketType(models.Model):
    _name = 'helpdesk.ticket.type'
    _description = 'Ticket Type'
    _order = "sequence"

    sequence = fields.Integer("Sequence")
    name = fields.Char("Name", required=True)
    worksheet_template_id = fields.Many2one("worksheet.template", string="Worksheet Template")
    company_id = fields.Many2one("res.company", string="Company")
