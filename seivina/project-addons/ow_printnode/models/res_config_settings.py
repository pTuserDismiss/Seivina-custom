# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    inspection_label_printer_blue_id = fields.Many2one(
        'printnode.printer',
        string="Printer for Blue Inspection Label",
        config_parameter='ow_printnode.inspection_label_printer_blue_id',
    )
    inspection_label_printer_white_id = fields.Many2one(
        'printnode.printer',
        string="Printer for White Inspection Label",
        config_parameter='ow_printnode.inspection_label_printer_white_id',
    )
    inspection_label_printer_yellow_id = fields.Many2one(
        'printnode.printer',
        string="Printer for Yellow Inspection Label",
        config_parameter='ow_printnode.inspection_label_printer_yellow_id',
    )
