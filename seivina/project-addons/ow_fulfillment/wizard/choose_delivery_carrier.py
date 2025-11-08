from odoo import api, fields, models


class ChooseDeliveryCarrier(models.TransientModel):
    _inherit = 'choose.delivery.carrier'

    top_3_rates = fields.Text(string='Top 3 Rates', readonly=True)

    @api.onchange('carrier_id')
    def _onchange_carrier_id(self):
        super()._onchange_carrier_id()
        self.top_3_rates = ""

    def _get_delivery_rate(self):
        vals = self.carrier_id.with_context(order_weight=self.total_weight).rate_shipment(self.order_id)
        if vals.get('success'):
            self.delivery_message = vals.get('warning_message', False)
            self.delivery_price = vals['price']
            self.display_price = vals['carrier_price']
            self.top_3_rates = vals.get('additional_info', False)
            return {'no_rate': vals.get('no_rate', False)}
        return {'error_message': vals['error_message']}
