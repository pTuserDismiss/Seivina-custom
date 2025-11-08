from odoo import models


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    def _get_shipping_dimensions_for_product(self, product):
        if product.shipping_length and product.shipping_width and product.shipping_height:
            return {
                'length': product.shipping_length,
                'width': product.shipping_width,
                'height': product.shipping_height,
                'volume': product.shipping_volume,
            }
        elif product.product_length and product.product_width and product.product_height:
            return {
                'length': product.product_length,
                'width': product.product_width,
                'height': product.product_height,
                'volume': product.volume,
            }
        else:
            return {
                'length': 1.0,
                'width': 1.0,
                'height': 1.0,
                'volume': 1.0,
            }

    def _calculate_shipping_dimensions_for_order(self, order):
        total_volume = 0.0
        max_length = 0.0
        max_width = 0.0
        max_height = 0.0
        
        for line in order.order_line:
            if line.product_id.type != 'service':
                product = line.product_id
                dimensions = self._get_shipping_dimensions_for_product(product)
                
                total_volume += dimensions['volume'] * line.product_uom_qty
                
                max_length = max(max_length, dimensions['length'])
                max_width = max(max_width, dimensions['width'])
                max_height = max(max_height, dimensions['height'])
        
        return {
            'length': max_length,
            'width': max_width,
            'height': max_height,
            'volume': total_volume,
        }
