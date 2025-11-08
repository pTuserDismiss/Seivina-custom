# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import AccessError


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

        if vals and any(k in vals for k in ['order_line', 'date_planned', 'notes']):
            is_admin = self.env.user._is_admin()
            if not is_admin:
                locked_records = self.filtered(lambda r: r.state in ['purchase', 'done'] and (r.has_alternatives or r.alternative_po_ids))
                if locked_records:
                    raise AccessError(_("You cannot modify this Purchase Order after approval in alternative flow."))

        return result
    
    @api.model
    def action_approve_compare_selection(self):
        active_po_id = self.env.context.get('purchase_order_id')
        if not active_po_id:
            return False
        po = self.env['purchase.order'].browse(active_po_id).exists()
        if not po:
            return False
        
        po.with_context(skip_alternative_check=True).button_confirm()
        return True


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def action_approve_compare_selection(self):
        for line in self:
            if line.order_id.state in ['draft', 'sent']:
                line.order_id.with_context(skip_alternative_check=True).button_confirm()
            else:
                line.order_id.button_approve()
