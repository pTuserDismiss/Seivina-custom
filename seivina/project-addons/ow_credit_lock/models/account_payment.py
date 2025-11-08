# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def action_post(self):
        res = super().action_post()
        orders = self.sale_deposit_id | (self.invoice_ids | self.reconciled_invoice_ids).line_ids.sale_line_ids.order_id
        orders._check_and_release_credit_lock()
        return res
