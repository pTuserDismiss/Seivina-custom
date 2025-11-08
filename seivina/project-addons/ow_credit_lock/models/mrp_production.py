# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import models, _
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _name = 'mrp.production'
    _inherit = ['mrp.production', 'credit.lock.mixin']

    def _get_backorder_mo_vals(self):
        # Backorder MOs should have the same Credit Lock status
        res = super()._get_backorder_mo_vals()
        res['credit_lock'] = self.credit_lock
        return res

    def button_mark_done(self):
        if self.filtered('credit_lock'):
            raise UserError(_('Cannot produce a manufacturing order in Credit Check Lock.\n'
                              'Please contact your administrator.'))
        return super().button_mark_done()

    def action_substitute(self):
        if self.credit_lock:
            raise UserError(_('Cannot add substitute since this manufacturing order is in Credit Check Lock.\n'
                              'Please contact your administrator.'))
        return super().action_substitute()

    def action_release_credit_lock(self, message=None):
        message = message or 'Sign-off for releasing manufacturing credit check lock'
        return super().action_release_credit_lock(message)

    def _activate_credit_lock(self):
        productions = super()._activate_credit_lock()
        self.picking_ids._activate_credit_lock()
        return productions

    def _release_credit_lock(self):
        productions = super()._release_credit_lock()
        self.picking_ids._release_credit_lock()
        # Auto reserve related transfers
        pickings = self.picking_ids.filtered(
            lambda r: r.state in ('waiting', 'confirmed')
                      and r.picking_type_id.reservation_method == 'at_confirm'
        )
        if pickings:
            pickings.action_assign()
        return productions

    def _eligible_for_credit_lock(self):
        self.ensure_one()
        orders = self._get_orders()
        return bool(orders.filtered('credit_lock'))
