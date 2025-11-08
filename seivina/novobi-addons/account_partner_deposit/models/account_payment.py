# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _, Command
from odoo.exceptions import ValidationError


class PaymentDeposit(models.Model):
    _inherit = 'account.payment'

    is_deposit = fields.Boolean('Is a Deposit?')

    property_account_customer_deposit_id = fields.Many2one(
        comodel_name='account.account',
        string='Customer Deposit Account',
        company_dependent=True,
        domain=[
            ('account_type', '=', 'liability_current'),
            ('deprecated', '=', False),
            ('reconcile', '=', True)
        ]
    )
    property_account_vendor_deposit_id = fields.Many2one(
        comodel_name='account.account',
        string='Vendor Deposit Account',
        company_dependent=True,
        domain=[
            ('account_type', '=', 'asset_prepayments'),
            ('deprecated', '=', False),
            ('reconcile', '=', True)
        ]
    )
    deposit_ids = fields.Many2many(
        comodel_name='account.move',
        string='Deposit Entries',
        help='Journal entries are created when reconciling invoices and deposits'
    )
    related_commercial_partner_id = fields.Many2one(
        related='partner_id.commercial_partner_id',
        string='Related Commercial Partner'
    )

    # -------------------------------------------------------------------------
    # ONCHANGE METHODS
    # -------------------------------------------------------------------------
    @api.onchange('partner_id')
    def _update_default_deposit_account(self):
        """
        Populate deposit account from contact
        """
        if self.partner_id and self.is_deposit:
            if self.partner_id.property_account_customer_deposit_id and self.partner_type == 'customer':
                self.property_account_customer_deposit_id = self.partner_id.property_account_customer_deposit_id.id
            elif self.partner_id.property_account_vendor_deposit_id and self.partner_type == 'supplier':
                self.property_account_vendor_deposit_id = self.partner_id.property_account_vendor_deposit_id.id

    # -------------------------------------------------------------------------
    # HELPERS
    # -------------------------------------------------------------------------
    @api.model
    def _get_trigger_fields_to_synchronize(self):
        deposit_fields = ('property_account_customer_deposit_id', 'property_account_vendor_deposit_id', 'is_deposit')
        return super()._get_trigger_fields_to_synchronize() + deposit_fields

    def _get_deposit_account(self):
        self.ensure_one()
        if self.partner_type == 'customer':
            return self.property_account_customer_deposit_id
        if self.partner_type == 'supplier':
            return self.property_account_vendor_deposit_id
        return self.env['account.account']

    def _prepare_move_line_default_vals(self, write_off_line_vals=None, force_balance=None):
        line_vals_list = super()._prepare_move_line_default_vals(write_off_line_vals, force_balance)
        if self.is_deposit:
            deposit_account = self._get_deposit_account()
            if not deposit_account:
                raise ValidationError(_('Deposit account has not been set'))
            line_vals_list[1]['account_id'] = deposit_account.id

        return line_vals_list

    def _validate_order_commercial_partner(self, order_field, model_name):
        """
        Helper method: Check if commercial partner of deposit is the same as the one of payment
        """
        for payment in self:
            commercial_partner = payment.partner_id.commercial_partner_id
            partner_type = order_field == 'sale_deposit_id' and 'customer' or 'vendor'
            if payment[order_field] and payment[order_field].partner_id.commercial_partner_id != commercial_partner:
                raise ValidationError(_('The {} of {} does not match with the one of deposit'.
                                        format(partner_type, model_name)))
