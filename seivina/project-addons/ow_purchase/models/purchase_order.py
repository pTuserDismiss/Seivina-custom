# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    company_purchase_attachment_ids = fields.Many2many(
        related='company_id.purchase_attachment_ids',
        string='Company Default Terms & Conditions',
        readonly=True
    )

    def write(self, vals):
        date_planned = vals.get('date_planned')
        result = super().write(vals)

        if date_planned:
            for order in self:
                sale_orders = order._get_sale_orders()
                if not sale_orders:
                    continue

                order_new_date = order.date_planned
                if not order_new_date:
                    continue

                for so in sale_orders:
                    so_delivery_date = so.commitment_date or so.expected_date

                    if so_delivery_date and order_new_date > so_delivery_date:
                        so.write({'commitment_date': order_new_date})
        return result
