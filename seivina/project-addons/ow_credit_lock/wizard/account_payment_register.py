# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import models


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def _reconcile_payments(self, to_process, edit_mode=False):
        super()._reconcile_payments(to_process, edit_mode=edit_mode)

        invoice_lines = self.env['account.move.line']
        for vals in to_process:
            invoice_lines |= vals['to_reconcile']

        orders = invoice_lines.move_id.line_ids.sale_line_ids.order_id
        orders._check_and_release_credit_lock()
