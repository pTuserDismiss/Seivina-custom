# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class DepositSalesOrder(models.Model):
    _inherit = 'sale.order'

    deposit_ids = fields.One2many(
        comodel_name='account.payment',
        inverse_name='sale_deposit_id',
        string='Deposits',
        domain=[('state', 'not in', ['draft', 'cancel']), ('is_deposit', '=', True)],
    )
    deposit_count = fields.Integer(string='Deposit Count', compute='_compute_deposit_amount')
    deposit_total = fields.Monetary(string='Total Deposit', compute='_compute_deposit_amount')
    remaining_total = fields.Monetary(string='Net Total', compute='_compute_deposit_amount')

    @api.depends('amount_total', 'deposit_ids', 'deposit_ids.state')
    def _compute_deposit_amount(self):
        for order in self:
            deposit_total = sum(order.deposit_ids.mapped('amount_company_currency_signed'))
            order.update({
                'deposit_total': deposit_total,
                'deposit_count': len(order.deposit_ids),
                'remaining_total': order.amount_total - deposit_total,
            })

    def action_view_deposit(self):
        action = self.env['ir.actions.act_window']._for_xml_id('account_partner_deposit.action_account_payment_customer_deposit')
        deposits = self.deposit_ids

        if len(deposits) == 1:
            form_view = [(self.env.ref('account_partner_deposit.view_account_payment_form_account_deposit').id, 'form')]
            action['res_id'] = self.deposit_ids.id
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
        else:
            action['domain'] = [('id', 'in', self.deposit_ids.ids)]

        return action

    def action_make_a_deposit(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('account_partner_deposit.action_order_make_deposit')
        action['context'] = dict(default_currency_id=self.currency_id.id)
        return action
