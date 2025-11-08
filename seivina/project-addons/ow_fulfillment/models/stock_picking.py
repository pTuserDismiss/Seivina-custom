from odoo import models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def prepare_dimensions_data(self, data, package, package_unit_default, package_code=False):
        data = super().prepare_dimensions_data(data, package, package_unit_default, package_code)
        dimensions = self.carrier_id._calculate_shipping_dimensions_for_order(self.sale_id)
        data.update({
            "dimensions": {
                "length": dimensions['length'],
                "width": dimensions['width'],
                "height": dimensions['height'],
            }
        })
        return data

    def action_put_in_pack(self):
        res = super(StockPicking, self).action_put_in_pack()
        wiz = self.env['choose.delivery.package'].sudo().browse(res['res_id'])
        wiz.shipping_weight = 0
        return res

    def ss_get_tracking_link(self):
        url_template = self.shipstation_carrier_id.tracking_url
        if url_template and self.carrier_tracking_ref:
            return url_template.format(TRACKING_NUMBER=self.carrier_tracking_ref)
        return False

    @api.depends('carrier_id', 'carrier_tracking_ref', 'freightview_shipmentDetailsUrl')
    def _compute_carrier_tracking_url(self):
        for picking in self:
            if picking.carrier_id.delivery_type == 'shipstation_ept':
                picking.carrier_tracking_url = picking.ss_get_tracking_link() or picking.carrier_tracking_url
            elif picking.carrier_id.delivery_type == 'freightview':
                picking.carrier_tracking_ref = 'Freightview'
                picking.carrier_tracking_url = picking.freightview_shipmentDetailsUrl or picking.carrier_tracking_url
            else:
                picking.carrier_tracking_url = super(StockPicking, self)._compute_carrier_tracking_url(picking)
