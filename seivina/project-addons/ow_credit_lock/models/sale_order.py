# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.tools import float_compare


class SalesOrder(models.Model):
    _name = 'sale.order'
    _inherit = ['sale.order', 'approval.button.mixin']

    credit_lock = fields.Boolean(string='Credit Locked', default=False, copy=False,
                                 help='Technical field to manage Delivery Credit Locked status')
    locked_delivery_count = fields.Integer(
        string='Count of Credit Locked Delivery Orders',
        compute='_compute_picking_ids'
    )

    locked_mrp_production_count = fields.Integer(
        string='Count of Credit Locked MO generated',
        compute='_compute_mrp_production_ids',
        compute_sudo=True,
    )

    # -------------------------------------------------------------------------
    # COMPUTE METHODS
    # -------------------------------------------------------------------------

    @api.depends('picking_ids')
    def _compute_picking_ids(self):
        super()._compute_picking_ids()
        for order in self:
            order.locked_delivery_count = len(order.picking_ids.filtered('credit_lock'))

    @api.depends('procurement_group_id.stock_move_ids.created_production_id.procurement_group_id.mrp_production_ids')
    def _compute_mrp_production_ids(self):
        super()._compute_mrp_production_ids()
        for record in self:
            record.locked_mrp_production_count = len(record.mrp_production_ids.filtered('credit_lock'))

    # -------------------------------------------------------------------------
    # ACTIONS
    # -------------------------------------------------------------------------

    def action_confirm(self):
        to_activate_orders = self.filtered('partner_credit_warning')
        res = super().action_confirm()

        # For orders that exceed Credit Limit, activate credit lock on order confirmation
        to_activate_orders._activate_credit_lock_deliveries()
        to_activate_orders._activate_credit_lock_productions()

        # Prepaid payments could be created for these orders in some cases:
        #    - Online deposit payments
        #    - A standalone deposit from Customer Deposits menu
        # Auto-release should be triggered on order confirmation to handle above cases
        to_activate_orders._check_and_release_credit_lock()

        return res
    
    def action_cancel(self):
        # Release credit lock on transfers, which will be cancelled after that
        self._release_credit_lock_deliveries()

        # Release credit lock on manufacturing orders
        # Also log message on chatter, since MOs are not automatically cancelled by OOTB
        for record in self:
            productions = record.mrp_production_ids.filtered('credit_lock')
            for production in productions:
                production._release_credit_lock()
                production.message_post(
                    body=_('Credit Lock is released since the sales order %s has been cancelled.',
                           record._get_html_link()),
                )
        return super().action_cancel()

    def _action_approval_wizard(self, **kwargs):
        self.ensure_one()
        new_wizard = self.env['approval.wizard'].create({
            'res_model': self._name,
            'res_id': self.id,
            'allowed_groups': 'ow_credit_lock.group_release_credit_lock',
            **kwargs,
        })
        return new_wizard._get_records_action(name=_('Sign-off Required'), target='new')

    def action_release_credit_lock_productions(self):
        self.ensure_one()
        return self._action_approval_wizard(
            reason=_('Sign-off for releasing manufacturing credit check lock'),
            method_approved='_release_credit_lock_productions'
        )

    def action_release_credit_lock_deliveries(self):
        self.ensure_one()
        return self._action_approval_wizard(
            reason=_('Sign-off for releasing delivery credit check lock'),
            method_approved='_release_credit_lock_deliveries'
        )

    # -------------------------------------------------------------------------
    # HELPER METHODS - Manual Credit Lock - Sales & Delivery Orders
    # -------------------------------------------------------------------------

    def _release_credit_lock_deliveries(self):
        self.filtered('credit_lock').write({'credit_lock': False})
        self.picking_ids._release_credit_lock()

    def _activate_credit_lock_deliveries(self):
        self.filtered(lambda r: not r.credit_lock).write({'credit_lock': True})
        self.picking_ids._activate_credit_lock()

    # -------------------------------------------------------------------------
    # HELPER METHODS - Manual Credit Lock - Manufacturing Orders
    # -------------------------------------------------------------------------

    def _release_credit_lock_productions(self):
        self.mrp_production_ids._release_credit_lock()

    def _activate_credit_lock_productions(self):
        self.mrp_production_ids._activate_credit_lock()

    # -------------------------------------------------------------------------
    # HELPER METHODS - Automatic Credit Lock
    # -------------------------------------------------------------------------

    def _check_and_release_credit_lock(self):
        for record in self:
            release_status = record.get_release_credit_lock_status()
            if release_status['production']:
                record._release_credit_lock_productions()
            if release_status['delivery']:
                record._release_credit_lock_deliveries()

    def get_release_credit_lock_status(self):
        self.ensure_one()
        payment_term = self.payment_term_id
        release_status = {
            'production': False,
            'delivery': False
        }
        if not payment_term:
            return release_status

        received_payment_amount = self.get_received_payments()
        expected_amount_by_terms = self.get_order_amount_by_terms()

        accumulated = 0.0
        TermLine = self.env['account.payment.term.line']

        for term_line_id, amount in expected_amount_by_terms.items():
            accumulated += amount
            term_line = TermLine.browse(term_line_id)
            if float_compare(accumulated, received_payment_amount, precision_digits=self.currency_id.decimal_places) != 1:
                release_status.update({
                    'production': release_status['production'] or term_line.auto_release_credit_lock_production,
                    'delivery': release_status['delivery'] or term_line.auto_release_credit_lock_delivery,
                })

        return release_status

    def get_order_amount_by_terms(self):
        payment_term = self.payment_term_id
        payment_term.ensure_one()

        terms = payment_term._compute_terms(
            date_ref=self.date_order or fields.Date.context_today(self),
            currency=self.currency_id,
            company=self.env.company,
            tax_amount=0,
            tax_amount_currency=0,
            untaxed_amount=self.amount_total,
            untaxed_amount_currency=self.amount_total,
            sign=1
        )

        return {
            term_line.id: terms['line_ids'][index]['company_amount'] for index, term_line in enumerate(payment_term.line_ids)
        }

    def get_received_payments(self):
        self.ensure_one()
        return self._get_received_deposits() + self._get_received_invoice_payments()

    def _get_received_deposits(self):
        self.ensure_one()
        payment_deposits = self.deposit_ids

        # The deposit amount is counted as invoice payment, if it has been applied to an invoice
        # Therefore, this amount needs to be exlucded from the total deposit
        applied_entry_deposits = payment_deposits.deposit_ids
        applied_deposit_amount = sum(applied_entry_deposits.mapped('amount_total'))

        return (self.deposit_total or 0.0) - applied_deposit_amount

    def _get_received_invoice_payments(self):
        invoices = self.order_line.invoice_lines.move_id
        need_residual_lines = invoices.line_ids.filtered(lambda line: line.account_id.reconcile
                                                                      or line.account_id.account_type in ('asset_cash', 'liability_credit_card'))
        total_amount = sum(need_residual_lines.mapped('debit'))
        total_residual = sum(need_residual_lines.mapped('amount_residual'))

        return total_amount - total_residual

