# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PaymentDeposit(models.Model):
    _inherit = 'account.payment'

    purchase_deposit_id = fields.Many2one(
        comodel_name='purchase.order',
        string='Purchase Order',
        domain="[('partner_id.commercial_partner_id', '=', related_commercial_partner_id), ('state', 'in', ['purchase', 'done'])]",
        help='Is this deposit made for a particular Purchase Order?'
    )

    @api.onchange('partner_id')
    def _onchange_purchase_deposit_partner_id(self):
        commercial_partner = self.partner_id.commercial_partner_id
        if self.purchase_deposit_id.partner_id.commercial_partner_id != commercial_partner:
            self.purchase_deposit_id = False

    def action_post(self):
        """Override"""
        # Check the vendor of deposit and order for the last time before validating
        self._validate_order_commercial_partner('purchase_deposit_id', 'Purchase Order')

        # Check if total deposit amount of an order has exceeded amount of this order
        for record in self.filtered(lambda r: r.purchase_deposit_id and r.state == 'draft'):
            order = record.purchase_deposit_id
            if order.currency_id.compare_amounts(record.amount_company_currency_signed, order.remaining_total) > 0:
                raise ValidationError(_('Total deposit amount cannot exceed purchase order amount'))

        return super().action_post()
