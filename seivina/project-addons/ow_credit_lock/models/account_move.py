# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def js_assign_outstanding_line(self, credit_aml_id):
        """
        Auto check and release Credit Lock when outstanding amount is reconciled with this invoice
        """
        res = super().js_assign_outstanding_line(credit_aml_id)
        orders = self.line_ids.sale_line_ids.order_id
        orders._check_and_release_credit_lock()
        return res
