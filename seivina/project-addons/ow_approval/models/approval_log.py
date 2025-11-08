# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ApprovalLog(models.Model):
    _name = 'approval.log'
    _inherit = 'approval.mixin'
    _description = 'Approval Log'
    _order = 'id desc'

    reviewer_uid = fields.Many2one(required=True)
    state = fields.Selection(
        selection=[
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        string='Status',
        default=False,
        copy=False,
    )
    error_msg = fields.Text(string='Error Message')

    @api.depends('res_model', 'res_id', 'state')
    def _compute_display_name(self):
        for log in self:
            log.display_name = f'{log.record and log.record.display_name or 'Undefined'}: {log.state.capitalize()}'
