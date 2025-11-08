from odoo import models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_default_carrier(self):
        # If Delivery Method is set in the sales order’s Delivery Address,
        # its parent, Customer, or Customer’s parent company: default to that Delivery Method
        # If not, set default Delivery Method using the same logic to set default Carrier for DO
        # based on product category defined at
        carriers = self.order_line.product_id._get_default_carrier()
        return self.partner_shipping_id.property_delivery_carrier_id \
                or self.partner_shipping_id.parent_id.property_delivery_carrier_id \
                or self.partner_id.property_delivery_carrier_id \
                or self.partner_id.parent_id.property_delivery_carrier_id \
                or (carriers and carriers.sorted('sequence')[0]) \
                or self.env['delivery.carrier']

    def action_open_delivery_wizard(self):
        view_id = self.env.ref('delivery.choose_delivery_carrier_view_form').id
        if self.env.context.get('carrier_recompute'):
            name = _('Update shipping cost')
            default_carrier = self.carrier_id
        else:
            name = _('Add a shipping method')
            default_carrier = self._get_default_carrier() or self.carrier_id
        return {
            'name': name,
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'choose.delivery.carrier',
            'view_id': view_id,
            'views': [(view_id, 'form')],
            'target': 'new',
            'context': {
                'default_order_id': self.id,
                'default_carrier_id': default_carrier.id,
                'default_total_weight': self._get_estimated_weight()
            }
        }

    def _auto_calculate_shipping_cost(self):
        self.ensure_one()
        
        default_carrier = self._get_default_carrier()
        if not default_carrier:
            raise UserError(_('No suitable shipping method found for this order.'))
        self.carrier_id = default_carrier

        shipping_price = 0.0
        
        rate = self.carrier_id.with_context(order_weight=self.shipping_weight).rate_shipment(self)
                
        if not rate.get('success'):
            raise UserError(_('Could not calculate shipping cost: %s') % rate.get('error_message', 'Unknown error'))
        
        shipping_price = rate.get('price', 0.0)

        existing_delivery_lines = self.order_line.filtered('is_delivery')
        if existing_delivery_lines:
            delivery_line = existing_delivery_lines[0]
            delivery_line.write({
                'product_id': self.carrier_id.product_id.id,
                'name': self.carrier_id.name,
                'price_unit': shipping_price,
                'product_uom_qty': 1.0,
                'product_uom': self.carrier_id.product_id.uom_id.id,
            })
        else:
            self._create_delivery_line(self.carrier_id, shipping_price)

    def action_confirm(self):
        if not self.env.context.get('confirm_with_shipping_wizard'):
            return super().action_confirm()
        
        wizard = self.env['shipping.confirmation.wizard'].create({
            'sale_order_id': self.id,
        })
        return wizard._get_records_action(
            name=_('Auto Calculate Shipping Cost'),
            target='new',
        )
