from odoo import _, api, fields, models


class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    scrap_reason_tag_ids = fields.Many2many(
        comodel_name='stock.scrap.reason.tag',
        string='Scrap Reason', required = True
    )
