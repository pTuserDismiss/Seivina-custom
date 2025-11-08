from odoo import api, fields, models, _


class ShippingConfirmationWizard(models.TransientModel):
    _name = 'shipping.confirmation.wizard'
    _description = 'Shipping Confirmation Wizard'

    sale_order_id = fields.Many2one('sale.order', string='Sale Order', required=True)

    def action_calculate_shipping_and_confirm(self):
        self.ensure_one()
        self.sale_order_id._auto_calculate_shipping_cost()
        self.sale_order_id.with_context(confirm_with_shipping_wizard=False).action_confirm()

    def action_confirm_only(self):
        self.ensure_one()
        self.sale_order_id.with_context(confirm_with_shipping_wizard=False).action_confirm()
