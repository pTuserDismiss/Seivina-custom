# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class ApprovalMixin(models.AbstractModel):
    _name = 'approval.mixin'
    _description = 'Approval Mixin'

    res_model = fields.Char(string='Related Model')
    res_id = fields.Integer(string='Related ID')
    reference = fields.Char(string='Related Document', compute='_compute_reference')

    reason = fields.Text(string='Reason', required=True)
    note = fields.Html(string='Notes')

    reviewer_uid = fields.Many2one(comodel_name='res.users', string='Reviewer')

    # Follow-up Actions
    method_approved = fields.Char(
        string='Python Execution Method (Approved)',
        help='The python method being executed on the target record, after this request is approved.'
    )
    method_rejected = fields.Char(
        string='Python Execution Method (Rejected)',
        help='The python method being executed on the target record, after this request is rejected.'
    )

    @property
    def record(self):
        if isinstance(self.res_model, str) and isinstance(self.res_id, int):
            return self.env[self.res_model].sudo().browse(self.res_id).exists()
        return False

    @api.depends('res_model', 'res_id')
    def _compute_reference(self):
        for record in self:
            record.reference = record.record and f'{record.res_model},{record.res_id}' or ''
