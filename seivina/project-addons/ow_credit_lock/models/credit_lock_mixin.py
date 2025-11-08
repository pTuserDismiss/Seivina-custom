# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CreditLockMixin(models.AbstractModel):
    _name = 'credit.lock.mixin'
    _inherit = 'approval.button.mixin'
    _description = 'Credit Lock Mixin'

    credit_lock = fields.Boolean(string='Credit Locked', default=False, copy=False, tracking=True)

    def _release_credit_lock(self):
        recs = self.filtered('credit_lock')
        recs.with_context(allow_write=True).write({'credit_lock': False})
        return recs

    def _activate_credit_lock(self):
        recs = self.filtered(lambda r: not r.credit_lock)
        recs.with_context(allow_write=True).write({'credit_lock': True})
        return recs

    def action_release_credit_lock(self, reason=None):
        self.ensure_one()
        new_wizard = self.env['approval.wizard'].create({
            'res_model': self._name,
            'res_id': self.id,
            'reason': reason,
            'method_approved': '_release_credit_lock',
            'allowed_groups': 'ow_credit_lock.group_release_credit_lock'
        })
        return new_wizard._get_records_action(name=_('Sign-off Required'), target='new')
    
    def action_activate_credit_lock(self):
        self._activate_credit_lock()

    @api.model_create_multi
    def create(self, vals_list):
        res = super(CreditLockMixin, self.with_context(allow_write=True)).create(vals_list)
        res.filtered(lambda r: r._eligible_for_credit_lock())._activate_credit_lock()
        return res

    def write(self, vals):
        if self.filtered('credit_lock') and not self._context.get('allow_write'):
            raise UserError(_('Cannot edit a record in Credit Check Lock.\nModel: {} ({})\n'
                              'Please contact your manager to release credit lock and update when needed.'.format(self._description, self._name)
                              ))
        # Add the context to ensure next triggered actions won't be blocked
        return super(CreditLockMixin, self.with_context(allow_write=True)).write(vals)

    def _eligible_for_credit_lock(self):
        self.ensure_one()
        # Override this to handle the logic for specific models
        return False
