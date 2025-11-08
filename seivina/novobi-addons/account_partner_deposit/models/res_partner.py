# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class Partner(models.Model):
    _inherit = 'res.partner'

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
    customer_deposit_aml_ids = fields.One2many(
        comodel_name='account.move.line',
        inverse_name='partner_id',
        domain=[
            ('payment_id.is_deposit', '=', True),
            ('payment_id.state', '=', 'posted'),
            ('payment_id.payment_type', '=', 'inbound'),
            ('reconciled', '=', False),
            ('credit', '>', 0), ('debit', '=', 0),
            '|', ('amount_residual', '!=', 0.0), ('amount_residual_currency', '!=', 0.0)
        ],
        help='This field only for customer deposit'
    )

    total_deposit = fields.Monetary(
        compute='_compute_total_deposit',
        groups='account.group_account_readonly,account.group_account_invoice'
    )
    
    @api.depends('customer_deposit_aml_ids')
    @api.depends_context('company', 'allowed_company_ids')
    def _compute_total_deposit(self):
        for partner in self:
            total_deposit = 0
            for aml in partner.customer_deposit_aml_ids:
                if aml.company_id == self.env.company and not aml.blocked:
                    total_deposit += aml.amount_currency
            partner.total_deposit = total_deposit
