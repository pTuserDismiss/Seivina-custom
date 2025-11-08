# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _
from odoo.exceptions import ValidationError


class ApprovalWizard(models.TransientModel):
    _name = 'approval.wizard'
    _inherit = 'approval.mixin'
    _description = 'Approval Wizard'

    pin = fields.Char(string='PIN Code')
    allowed_groups = fields.Char(
        string='Restricted Groups',
        help='If set, only employees with related users belong to these groups are allowed to approve/reject a request\n'
             'The groups are identified by external id, and separated by comma'
    )

    def _get_reviewer(self):
        return self.env['hr.employee'].sudo().search([('pin', '=', self.pin)], limit=1)

    def _validate_reviewer(self):
        self.ensure_one()
        if not self.pin:
            raise ValidationError(_('The PIN Code must be set.'))

        emp_reviewer = self._get_reviewer()
        if not emp_reviewer:
            raise ValidationError(_('The PIN Code cannot be found.'))
        reviewer = emp_reviewer.user_id
        if not reviewer:
            raise ValidationError(_('The Employee must have the associated system user. Please contact your Administrator.'))
        if self.allowed_groups and not reviewer.has_groups(self.allowed_groups):
            raise ValidationError(_('The employee of the PIN code does not have right to approve.'))

        self.reviewer_uid = reviewer
        return True

    def _prepare_approval_log_vals(self):
        self.ensure_one()
        return {
            'res_model': self.res_model,
            'res_id': self.res_id,
            'reviewer_uid': self.reviewer_uid.id,
            'reason': self.reason,
            'note': self.note,
            'method_approved': self.method_approved,
            'method_rejected': self.method_rejected,
        }

    def _create_approval_log(self, **kwargs):
        self.ensure_one()
        approval_log_val = self._prepare_approval_log_vals()
        record = self.record
        if not record:
            kwargs['error_msg'] = _(f'Cannot find the record (Model: {self.res_model}, ID: {self.res_id}) to perform the action.')
        elif (
                kwargs.get('state') == 'approved'
                and isinstance(self.method_approved, str)
                and not hasattr(record, self.method_approved)
        ):
            kwargs['error_msg'] = _(f'Cannot perform the action <{self.method_approved}> on record <{record.display_name}>')
        elif (
                kwargs.get('state') == 'rejected'
                and isinstance(self.method_rejected, str)
                and not hasattr(record, self.method_rejected)
        ):
            kwargs['error_msg'] = _(f'Cannot perform the action <{self.method_rejected}> on the record <{record.display_name}>')

        approval_log_val.update(kwargs)
        return self.env['approval.log'].create(approval_log_val)

    def action_approve(self):
        self.ensure_one()
        self._validate_reviewer()
        self._create_approval_log(state='approved')
        try:
            getattr(self.record.with_user(self.reviewer_uid), self.method_approved or '')()
        except AttributeError:
            pass

    def action_reject(self):
        self.ensure_one()
        self._validate_reviewer()
        self._create_approval_log(state='rejected')
        try:
            getattr(self.record.with_user(self.reviewer_uid), self.method_rejected or '')()
        except AttributeError:
            pass
