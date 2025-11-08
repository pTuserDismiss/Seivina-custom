from odoo import models

from odoo.addons.shipstation_ept.models.stock_backorder_confirmation import StockBackorderConfirmation as ShipstationStockBackorderConfirmation


class StockBackorderConfirmation(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'

    def process(self):
        """
        In backorder set some fields value after super method called.
        - is_exported_to_shipstation set as true because in shipstation order get split so its
        already exported in shipstation.
        - exported_order_to_shipstation in backorder had to set parent or else we can say that
        first out picking's export order name because from shipstation have to get order response
        from that name.
        """
        # OAK-202: Fix for backorder confirmation
        # --- Customization: get the pickings to validate from the context
        res = super(ShipstationStockBackorderConfirmation, self).process()
        pickings_to_validate_ids = self.env.context.get('button_validate_picking_ids')
        pickings_to_validate = self.env['stock.picking'].browse(pickings_to_validate_ids) if pickings_to_validate_ids else self.env['stock.picking']
        # --- End Customization
        for picking in pickings_to_validate:
            picking_ids = False
            if picking.sale_id:
                picking_ids = picking.sale_id.picking_ids
            elif picking.backorder_ids:
                backorder = picking.backorder_id
                picking_backorder = backorder

                while backorder:
                    new_backorder = backorder.backorder_id
                    if new_backorder:
                        picking_backorder += new_backorder
                        backorder = new_backorder
                    else:
                        break
                picking_ids = picking + picking.backorder_ids + picking_backorder

            if picking_ids and picking.is_exported_to_shipstation:
                out_picking = picking_ids.filtered(lambda pick: pick.picking_type_id.code == "outgoing")
                if out_picking:
                    picking.backorder_ids.write({
                        'is_exported_to_shipstation': True,
                        'exported_order_to_shipstation': out_picking.sorted('id')[0].prepare_export_order_name()
                    })
        return res
