# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class AccountPaymentTermLine(models.Model):
    _inherit = 'account.payment.term.line'

    auto_release_credit_lock_production = fields.Boolean(string='Auto Release Manufacturing Lock', default=False)
    auto_release_credit_lock_delivery = fields.Boolean(string='Auto Release Delivery Lock', default=False)
