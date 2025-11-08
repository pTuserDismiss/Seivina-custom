# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def write(self, vals):
        res = super().write(vals)

        if vals.get("state") == "sent":
            orders = self.filtered(
                lambda order: not order.opportunity_id
                and order.website_id.generate_opportunity
                and order.transaction_ids.filtered(
                    lambda transaction: transaction.state == "pending"
                )
            )

            leads_vals_lst = [
                {
                    "name": order.name,
                    "partner_id": order.partner_id.id,
                    "email_from": order.partner_id.email,
                    "phone": order.partner_id.phone,
                    "user_id": order.user_id.id,
                    "team_id": order.team_id.id,
                    "company_id": order.company_id.id,
                    "order_ids": order.ids,
                }
                for order in orders
            ]

            self.env["crm.lead"].create(leads_vals_lst)

        return res
