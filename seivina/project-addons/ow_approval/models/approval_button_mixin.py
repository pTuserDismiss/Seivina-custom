# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _


class ApprovalButtonMixin(models.AbstractModel):
    _name = 'approval.button.mixin'
    _description = 'Approval Button Mixin'

    approval_logs_count = fields.Integer('Approval Log Count', compute='_compute_approval_logs_count')

    def _get_approval_logs_domain(self):
        return [('res_model', '=', self._name), ('res_id', 'in', self.ids)]

    def _compute_approval_logs_count(self):
        approval_log_groups = self.env['approval.log']._read_group(
            domain=self._get_approval_logs_domain(),
            groupby=['res_id'],
            aggregates=['__count']
        )
        count = {res_id: count for res_id, count in approval_log_groups}
        for record in self:
            record.approval_logs_count = count.get(record.id, 0)

    def action_view_approval_logs(self):
        logs = self.env['approval.log'].search(self._get_approval_logs_domain())
        return logs._get_records_action(name=_('Approval Logs'))
