from odoo import _, api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    show_inspection_label = fields.Boolean(related='picking_id.picking_type_id.show_inspection_label')
    inspection_label = fields.Selection(related='product_id.product_tmpl_id.inspection_label')
