# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def find_if_shipped_and_fetch_tracking_number(self):
        """
        Override to get the ShipStation ShipmentID from the shipment response
        and store it in the picking for later use, such as voiding label from Odoo
        """
        instance = self.shipstation_instance_id
        tracking_number = ''
        shipping_cost = 0

        # OAK-127: Cannot cancel the shipping label when exporting the order to Shipstation
        # --- Customization: Store the ShipStation ShipmentID
        shipment_id = False
        # --- End Customization

        # For backorder find first picking export order name to get order response from shipstation.
        order_number = self.prepare_export_order_name() if not self.exported_order_to_shipstation else self.exported_order_to_shipstation
        url = '/orders'
        querystring = {'orderNumber': order_number}
        response, code = instance.get_connection(url=url, data=None, params=querystring, method="GET")

        if code.status_code != 200:
            try:
                res = json.loads(code.content.decode('utf-8')).get('ExceptionMessage')
            except:
                res = code.content.decode('utf-8')
            msg = "While requesting for order status of {} on shipstation: {}".format(self.name, res)
            self.unlink_old_message_and_post_new_message(body=msg)
            _logger.info(msg)
            return False, response

        if len(response.get('orders')) > 1:
            # Checked all orders are in waiting state then directly return from here & send message.
            check_order_status_waiting = all(
                res.get('orderStatus') == 'awaiting_shipment' for res in response.get('orders'))
            if check_order_status_waiting:
                self.unlink_old_message_and_post_new_message(body="Order has not been shipped on the shipstation.")
                _logger.info("Order: %s has not been shipped on the shipstation.", self.name)
                return False, response

            # Checked all orders are in cancel state then cancel picking order from here.
            check_order_status_cancel_all = all(res.get('orderStatus') == 'cancelled' for res in response.get('orders'))
            if check_order_status_cancel_all:
                self.action_cancel()
                return False, response

            # From response set sorting to set shipped order first & execute it first.
            order_number_response = sorted(response.get('orders'), key=lambda d: d['orderStatus'] != 'shipped')
            for response_val in order_number_response:
                # Checked that picking already validated or not.
                exist_bo_id = self.env['stock.picking'].search([
                    ('validated_shipstation_order_id', '=', response_val.get('orderId'))])
                if not exist_bo_id and not self.validated_shipstation_order_id:
                    if response_val.get('orderStatus', '') == 'shipped' and self.state == 'assigned':
                        self.is_get_shipping_label = True
                        for back_line in self.move_ids:
                            is_item_in_responce = False
                            for item in response_val.get('items'):
                                if item.get('sku', '') == back_line.product_id.default_code:
                                    is_item_in_responce = True
                                    back_line.write({
                                        'quantity': item.get('quantity'),
                                        'picked': True
                                    })
                                    if not self.validated_shipstation_order_id:
                                        self.write({
                                            'validated_shipstation_order_id': response_val.get('orderId'),
                                            'shipstation_order_id': response_val.get('orderId')
                                        })
                            if not is_item_in_responce:
                                back_line.write({'quantity': 0})
                        # Get Tracking Reference
                        ship_url = '/shipments?orderId=%s' % response_val.get('orderId', False)
                        shipment_response, code = instance.get_connection(url=ship_url, data=None, params=None, method="GET")
                        if code.status_code != 200:
                            try:
                                res = json.loads(code.content.decode('utf-8')).get(
                                    'ExceptionMessage')
                            except:
                                res = code.content.decode('utf-8')
                            msg = 'While requesting for tracking number of %s on Shipstation: %s' % (self.name, res)
                            self.unlink_old_message_and_post_new_message(body=msg)
                            _logger.exception(msg)
                            return False, shipment_response

                        if self.sale_id.team_id.shipstation_update_carrier:
                            self.set_carrier_based_on_response(shipment_response)

                        for shipment in shipment_response.get('shipments'):
                            if str(shipment.get('voided', '')).lower() == 'true':
                                continue
                            tracking_number = shipment.get('trackingNumber', False)
                            shipping_cost += shipment.get('shipmentCost', 0)

                            # OAK-127: Cannot cancel the shipping label when exporting the order to Shipstation
                            # --- Customization: Store the ShipStation ShipmentID
                            shipment_id = shipment.get('shipmentId', False)
                            # --- End Customization

                            if self.shipstation_order_id:
                                self.shipstation_order_id = response_val.get('orderId')
                    elif response_val.get('orderStatus') == 'cancelled':
                        check_order_status_waiting_any = any(
                            res.get('orderStatus') == 'awaiting_shipment' for res in response.get('orders'))
                        # Checked if any other order still in waiting state in shipstation then
                        # return from here & send message.
                        if check_order_status_waiting_any:
                            self.unlink_old_message_and_post_new_message(
                                body="Label has not been generated on the shipstation.")
                            _logger.info(
                                "Label has not been generated on the shipstation for picking:"
                                " %s", self.name)
                            return False, response
                        cancel_status = self.action_cancel()
                        # If cancel process succeed then update shipstation order id value.
                        if cancel_status:
                            self.write({'shipstation_order_id': response_val.get('orderId')})
                        return False, response
                    elif not self.validated_shipstation_order_id:
                        self.unlink_old_message_and_post_new_message(
                            body="Label has not been generated on the shipstation.")
                        _logger.info("Label has not been generated on the shipstation for picking:"
                                     " %s", self.name)
                        return False, response
        elif len(response.get('orders')) == 1:
            """
            Modify By - Vaibhav Chadaniya
            15556: Avoid duplicate call & Get shipstation order id from response (In Single Order Case)
            Remove the duplicate call to retrieve the order from the initial API response.
            """
            response_order = response.get('orders')[0]
            if code.status_code != 200:
                try:
                    res = json.loads(code.content.decode('utf-8')).get('ExceptionMessage')
                except:
                    res = code.content.decode('utf-8')
                msg = "While requesting for order status of {} on shipstation: {}".format(
                    self.name, res)
                self.unlink_old_message_and_post_new_message(body=msg)
                if self.batch_id:
                    self.batch_id.unlink_old_message_and_post_new_message(
                        body="While requesting for order status of {} on shipstation: {}".format(
                            self.name, res))
                _logger.info(msg)
                return False, response

            if response_order.get('orderStatus') == 'cancelled':
                self.action_cancel()
                return False, response

            if not response_order.get('orderStatus') == 'shipped':
                self.unlink_old_message_and_post_new_message(body="Label has not been generated on the shipstation.")
                if self.batch_id:
                    self.batch_id.unlink_old_message_and_post_new_message(
                        body="Label has not been generated for {} on the shipstation.".format(self.name))
                _logger.info("Label has not been generated on the shipstation for picking: %s", self.name)
                return False, response

            self.is_get_shipping_label = True
            url = '/shipments?orderId=%s' % response_order.get('orderId', self.shipstation_order_id)
            response, code = instance.get_connection(url=url, data=None, params=None, method="GET")
            if code.status_code != 200:
                try:
                    res = json.loads(code.content.decode('utf-8')).get('ExceptionMessage')
                except:
                    res = code.content.decode('utf-8')
                msg = 'While requesting for Tracking number of %s on Shipstation' \
                      '\n%s' % (self.name, res)
                self.unlink_old_message_and_post_new_message(body=msg)
                if self.batch_id:
                    self.batch_id.unlink_old_message_and_post_new_message(body=msg)
                _logger.exception(msg)
                return False, response

            if self.sale_id.team_id.shipstation_update_carrier:
                self.set_carrier_based_on_response(response)

            for shipment in response.get('shipments'):
                # OAK-127: Cannot cancel the shipping label when exporting the order to Shipstation
                # --- Customization: Store the ShipStation ShipmentID
                shipment_id = shipment.get('shipmentId')
                # --- End Customization

                if str(shipment.get('voided', '')).lower() == 'true':
                    continue
                tracking_number += ', {}'.format(
                    shipment.get('trackingNumber', '')) if tracking_number else shipment.get('trackingNumber', '')
                shipping_cost += shipment.get('shipmentCost', 0)
        else:
            msg = "While requesting for order {} not found on shipstation".format(self.name)
            self.unlink_old_message_and_post_new_message(body=msg)
            return False, response
        shipping_cost = self.convert_company_currency_amount_to_order_currency(shipping_cost)
        self.write({
            'shipstaion_actual_shipping_cost': shipping_cost,

            # OAK-127: Cannot cancel the shipping label when exporting the order to Shipstation
            # --- Customization: Store the ShipStation ShipmentID
            'carrier_tracking_ref': tracking_number if tracking_number else self.carrier_tracking_ref,
            'shipstation_shipment_id': shipment_id if shipment_id else self.shipstation_shipment_id,
            # --- End Customization
        })
        return True, response
