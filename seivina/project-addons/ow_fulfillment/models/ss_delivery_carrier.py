from odoo import models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round


class ShipstationDeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    def shipstation_ept_rate_shipment(self, orders):
        orders.ensure_one()
        price = 0.0
        rates = self._get_shipstation_rates(orders)
        if not rates:
            raise UserError('No rates returned from ShipStation. Please check your configuration and try again.')
        
        filtered_rates = self._filter_and_sort_shipstation_rates(rates)
        top_3_rates = filtered_rates[:3]
        
        if len(top_3_rates) == 0:
            average_rate = 0
        else:
            average_rate = sum(rate['price'] for rate in top_3_rates) / len(top_3_rates)

        additional_info = ''
        if self.get_cheapest_rates:
            for index, rate in enumerate(top_3_rates):
                rate_price = float_round(rate['price'], precision_digits=2)
                additional_info += f'Top {index+1} rate: ${rate_price} - Service: {rate.get('serviceDescription', 'N/A')} - Carrier: {rate.get('carrier', 'N/A')}\n'
        
        price = average_rate

        return {
            'success': True,
            'price': price,
            'error_message': False,
            'warning_message': False,
            'additional_info': additional_info,
        }

    def _get_shipstation_rates(self, order):
        ################################################
        # OAK-163: get shipstation rates
        # This method gets the shipstation rates for the order
        # If cheapest rates are enabled, it will get the cheapest rates
        # Otherwise, it will get the rates for the selected service and package
        ################################################
        shipstation_warehouse = self.env['shipstation.warehouse.ept'].search(
            ['|', ('odoo_warehouse_id', '=', order.warehouse_id.id),
                ('is_default', '=', True),
                ('shipstation_instance_id', '=', self.shipstation_instance_id.id)], limit=1)
        
        if not shipstation_warehouse:
            raise UserError('Warehouse configuration not found for ShipStation.')
        
        shipstation_carriers = self.shipstation_carrier_ids if self.get_cheapest_rates else self.shipstation_carrier_id
        all_rates = []

        data = {'packageCode': self.shipstation_package_id.shipper_package_code or 'package'}
        if not self.get_cheapest_rates:
            data.update({'serviceCode': self.shipstation_service_id.service_code})

        for carrier in shipstation_carriers:
            shipping_dimensions = self._calculate_shipping_dimensions_for_order(order)
            data = self.get_data(data, carrier, shipstation_warehouse, order.partner_shipping_id, 
                                self._calculate_order_weight(order))
            data['dimensions']['length'] = shipping_dimensions['length']
            data['dimensions']['width'] = shipping_dimensions['width']
            data['dimensions']['height'] = shipping_dimensions['height']
            
            querystring = {'carrierCode': carrier.code}
            response, code = self.shipstation_instance_id.get_connection(
                url='/shipments/getrates', data=data, params=querystring, method='POST')
            
            if response and code.status_code == 200:
                for result in response:
                    price = result.get('shipmentCost', 0)
                    other_cost = result.get('otherCost', 0)
                    total_price = price + other_cost
                    
                    if total_price > 0:
                        all_rates.append({
                            'price': total_price,
                            'servicecode': result.get('serviceCode', ''),
                            'carrier': carrier.name,
                            'serviceDescription': result.get('serviceName', '')
                        })
        return all_rates

    def _filter_and_sort_shipstation_rates(self, rates):
        filtered_rates = []
        for rate in rates:
            if not rate.get('price') or rate.get('price') <= 0:
                continue
                
            service_name = rate.get('serviceDescription', '').lower()
            
            # OAK-163: filter out next day rates
            if any(keyword in service_name for keyword in ['next day']):
                continue

            filtered_rates.append(rate)
        
        filtered_rates.sort(key=lambda x: x['price'], reverse=True)
        
        return filtered_rates

    def _calculate_order_weight(self, order):
        ################################################
        # OAK-163: calculate order weight
        # This method calculates the total weight of the order
        ################################################
        if self.env.context.get('order_weight'):
            total_weight = self.env.context.get('order_weight')
        else:
            total_weight = sum([(line.product_id.weight * line.product_uom_qty) for line in order.order_line]) or 0.0
        
        try:
            total_weight = self.convert_weight_for_shipstation(
                order.company_id and order.company_id.get_weight_uom_id(),
                self.shipstation_instance_id.weight_uom_id, total_weight)
        except Exception as e:
            total_weight = 1.0
            
        return total_weight 
