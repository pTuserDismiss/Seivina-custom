# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _create_payment(self, **extra_create_values):
        orders = self.sale_order_ids
        if len(orders) == 1:
            extra_create_values.update({
                'is_deposit': True,
                'sale_deposit_id': orders.id,
                'property_account_customer_deposit_id': self.partner_id.property_account_customer_deposit_id.id,
            })
        return super()._create_payment(**extra_create_values)
