from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    total_quote_quantity_threshold = fields.Float(
        related='company_id.total_quote_quantity_threshold',
        string='Total Quote Qty Greater Than',
        readonly=False,
    )
    probability_threshold = fields.Float(
        related='company_id.probability_threshold',
        string='Probability Greater Than',
        readonly=False,
    )
