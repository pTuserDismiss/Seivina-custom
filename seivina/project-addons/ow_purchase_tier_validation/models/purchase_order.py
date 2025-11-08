from odoo import models, fields
from datetime import datetime, timedelta


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    # Override tier validation function
    def evaluate_tier(self, tier):
        res = super().evaluate_tier(tier)
        if res and tier.additional_conditions == 'total_amount_spent_over_period_of_time':
            total_amount = res.get_total_purchase_amount_for_period(tier.period)
            if total_amount < tier.amount:
                return self.env['purchase.order']
            else:
                return res
        return res
    
    def get_total_purchase_amount_for_period(self, period):
        current_date = fields.Date.context_today(self)
        start_date = current_date - timedelta(days=period)
        purchase_orders = self.env['purchase.order'].search([
            ('state', '=', 'purchase'), 
            ('date_approve', '>=', start_date)
        ])
        total_amount = sum(purchase_orders.mapped('amount_total'))

        return total_amount
