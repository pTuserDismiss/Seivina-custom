from odoo import models, fields

class PickingType(models.Model):
    _inherit = 'stock.picking.type'

    show_inspection_label = fields.Boolean("Show Inspection Label", default=True)
