import requests

from odoo import api, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round

from odoo.addons.freightview_delivery_carrier.models.freightview_api import FreightviewAPI

##################################################################################################
# NOVOBI CUSTOMIZATION: Monkey patch to remove carriers from query params
# This is to avoid the issue where the necessary carriers are not included in the query params
##################################################################################################
def get_freightview_query_params(self, delivery_obj, timeout):
    return f"?timeout={timeout}"

FreightviewAPI.get_freightview_query_params = get_freightview_query_params
##################################################################################################

class FreightviewDeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    @api.model
    def freightview_rate_shipment(self, order):
        '''
        Calculate shipping cost for FreightView connector based on the new requirements:
        1. Take top 3 highest rates (excluding Next Day shipping)
        2. Calculate the average of the 3
        3. Add Additional Margin and Margin on Rate %
        4. If there's no rate returned, raise error
        '''
        rates = self._get_freightview_rates(order) 
        if not rates:
            raise UserError('No rates returned from FreightView. Please check your configuration and try again.')
        
        filtered_rates = self._filter_and_sort_rates(rates)
        top_3_rates = filtered_rates[:3]
        
        if len(top_3_rates) == 0:
            average_rate = 0
        else:
            average_rate = sum(rate['total'] for rate in top_3_rates) / len(top_3_rates)

        additional_info = ''
        for index, rate in enumerate(top_3_rates):
            rate_price = float_round(rate['total'], precision_digits=2)
            additional_info += f'Top {index+1} rate: ${rate_price} - Service: {rate['serviceDescription']} - Carrier: {rate['carrier']}\n'
        
        return {
            'success': True,
            'price': average_rate,
            'error_message': False,
            'warning_message': False,
            'additional_info': additional_info,
        }

    def _get_freightview_rates(self, order):
        picking = self._create_simple_picking_for_rates(order)
        rates_url = self._get_freightview_rates_url(picking)
        if not rates_url:
            picking.unlink()
            raise UserError('Could not obtain rates URL from FreightView')
        
        rates_response = self._fetch_rates_from_url(picking, order.currency_id.name)
        
        picking.unlink()
        
        return rates_response

    def _get_freightview_rates_url(self, picking):
        currency_id = self.get_shipment_currency_id(pickings=picking)
        currency_code = currency_id.name
        config = self.wk_get_carrier_settings([
            'freightview_client_id', 'freightview_client_secret', 
            'freightview_user_api_key', 'freightview_account_api_key',
            'freightview_grant_type', 'freightview_timeout', 'prod_environment',
        ])
        
        config['freightview_enviroment'] = 'production' if config['prod_environment'] else 'test'
        config['freightview_currency'] = currency_code
        config['freightview_shipment_type'] = picking.freightview_shipment_type
        
        sdk = FreightviewAPI(**config)
        auth_header = sdk.get_freightview_auth_header(config.get('freightview_account_api_key'))
        
        if not self.freightview_carrier_ids:
            raise UserError('No carrier set for this freightview delivery method!')
        
        query_param = sdk.get_freightview_query_params(self, self.freightview_timeout or 30)
        request_body = self.get_freightview_request_body(sdk, picking, currency_code)
        try:
            rates_url = sdk.get_freightview_book_url(auth_header, query_param, request_body)
            return rates_url
        except Exception as e:
            raise UserError(f'Error getting rates URL: {str(e)}')

    def _fetch_rates_from_url(self, picking, currency_code):
        '''
        Fetch rates from the FreightView rates URL
        '''
        try:
            config = self.wk_get_carrier_settings([
                'freightview_client_id', 'freightview_client_secret', 
                'freightview_user_api_key', 'freightview_account_api_key',
                'freightview_grant_type', 'freightview_timeout', 'prod_environment'
            ])
            
            config['freightview_enviroment'] = 'production' if config['prod_environment'] else 'test'
            config['freightview_shipment_type'] = 'ltl'
            
            sdk = FreightviewAPI(**config)
            url = sdk.APIEND['sandbox' if config['freightview_enviroment']=='test' else 'production']['rate_ltl']
            request_body = self.get_freightview_request_body(sdk, picking, currency_code)
            
            res = requests.post(url + sdk.get_freightview_query_params(self,15),
                                headers=sdk.get_freightview_auth_header(config.get('freightview_account_api_key')), json=request_body, timeout=30)
            if res.status_code != 200:
                raise UserError(f'FreightView rate API error: {res.status_code} {res.text}')
            data = res.json()
            rates = data.get('rates') or data.get('quotes') or []
            
            return rates
            
        except Exception as e:
            raise UserError(f'Error fetching rates from FreightView: {str(e)}')

    def _filter_and_sort_rates(self, rates):
        filtered_rates = []
        for rate in rates:
            service_name = rate.get('serviceDescription', '').lower()
            if not any(keyword in service_name for keyword in ['next day']) and rate.get('status') == 'ok':
                filtered_rates.append(rate)
        
        filtered_rates.sort(key=lambda x: x['total'], reverse=True)
        
        return filtered_rates

    def _apply_margins(self, base_rate):
        if self.margin > 0:
            base_rate += base_rate * self.margin
        
        if self.fixed_margin > 0:
            base_rate += self.fixed_margin
        
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        return round(base_rate, precision)

    def get_freightview_items(self, pickings, currency_code=None):
        '''
        Get freight items for FreightView API without requiring complex package creation
        '''
        result = dict()
        packages = []

        if self.env.context.get('order_weight'):
            total_weight = self.env.context.get('order_weight')
        else:
            total_weight = 0
            for move in pickings.move_ids:
                if move.product_id.weight:
                    total_weight += move.product_id.weight * move.quantity

        total_weight = max(total_weight, 1.0)
        
        order = self.env['sale.order'].search([('name', '=', pickings.origin)], limit=1)
        if order:
            shipping_dimensions = self._calculate_shipping_dimensions_for_order(order)
        else:
            shipping_dimensions = {
                'length': 1.0,
                'width': 1.0,
                'height': 1.0,
                'volume': 1.0,
            }
        
        default_packaging = self.packaging_id.package_type_id if self.packaging_id else None
        if not default_packaging:
            default_packaging = self.env['stock.package.type'].search([
                ('package_carrier_type', '=', 'freightview')
            ], limit=1)
        
        if not default_packaging:
            default_packaging = self.env['stock.package.type'].create({
                'name': 'Default FreightView Package',
                'package_carrier_type': 'freightview',
                'max_weight': 1000,
                'width': shipping_dimensions['width'],
                'packaging_length': shipping_dimensions['length'],
            })
        
        package_data = dict(
            description=f'Package for {pickings.name}',
            weight=total_weight,
            dimensions=dict(
                length=shipping_dimensions['length'],
                width=shipping_dimensions['width'],
                height=shipping_dimensions['height'],
            ),
        )
        packages.append(package_data)
        
        result['packages'] = packages
        result['total_package'] = 1
        result['declared_value'] = 0  
        result['total_weight'] = round(total_weight)
        result['package'] = default_packaging.name
        
        return result

    def _create_simple_picking_for_rates(self, order):
        picking_vals = {
            'partner_id': order.partner_shipping_id.id,
            'picking_type_id': self.env['stock.picking.type'].search([
                ('code', '=', 'outgoing'),
                ('warehouse_id', '=', order.warehouse_id.id)
            ], limit=1).id,
            'location_id': order.warehouse_id.lot_stock_id.id,
            'location_dest_id': order.warehouse_id.lot_stock_id.id,
            'carrier_id': self.id,
        }
        
        picking = self.env['stock.picking'].create(picking_vals)
        
        for line in order.order_line:
            if line.product_id.type != 'service':
                self.env['stock.move'].create({
                    'name': line.product_id.name,
                    'product_id': line.product_id.id,
                    'quantity': line.product_uom_qty,
                    'product_uom': line.product_uom.id,
                    'picking_id': picking.id,
                    'location_id': picking.location_id.id,
                    'location_dest_id': picking.location_dest_id.id,
                })
        
        return picking
