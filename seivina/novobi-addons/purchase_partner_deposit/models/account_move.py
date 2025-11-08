# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        """
        Override
        Reconcile vendor deposits with bill automatically
        """
        res = super().action_post()

        for bill in self.filtered(lambda r: r.move_type == 'in_invoice'):
            deposits = bill.invoice_line_ids.mapped('purchase_line_id.order_id.deposit_ids')
            self._reconcile_deposit(deposits, bill)

        return res
