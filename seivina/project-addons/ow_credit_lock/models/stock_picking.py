# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class StockPicking(models.Model):
    _name = 'stock.picking'
    _inherit = ['stock.picking', 'credit.lock.mixin']

    def action_release_credit_lock(self, message=None):
        message = message or 'Sign-off for releasing delivery credit check lock'
        return super().action_release_credit_lock(message)

    def _release_credit_lock(self):
        pickings = super()._release_credit_lock()
        # If a picking of a sales order is released, also release the order so next pickings
        # are released by default.
        if pickings.sale_id:
            pickings.sale_id._release_credit_lock_deliveries()
        # Auto reserve the transfer
        to_assign = self.filtered(
            lambda r: r.state in ('waiting', 'confirmed')
                      and r.picking_type_id.reservation_method == 'at_confirm'
        )
        if to_assign:
            to_assign.action_assign()
        return pickings

    def _activate_credit_lock(self):
        pickings = super()._activate_credit_lock()
        # If a picking of a sales order is locked, also lock the order so next pickings
        # are locked by default.
        if pickings.sale_id:
            pickings.sale_id._activate_credit_lock_deliveries()
        return pickings

    def _eligible_for_credit_lock(self):
        self.ensure_one()
        return self.sale_id.credit_lock

