from collections import defaultdict
from odoo import fields, models, api


class ProductLabelLayout(models.TransientModel):
    _inherit = 'product.label.layout'

    @api.onchange('product_to_print_id', 'print_format')
    def onchange_product_to_print_id(self):
        match self.product_to_print_id.inspection_label:
            case 'blue':
                printer_blue = self.env['ir.config_parameter'].sudo().get_param('ow_printnode.inspection_label_printer_blue_id')
                self.printer_id = self.env['printnode.printer'].browse(int(printer_blue))
            case 'white':
                printer_white = self.env['ir.config_parameter'].sudo().get_param('ow_printnode.inspection_label_printer_white_id')
                self.printer_id = self.env['printnode.printer'].browse(int(printer_white))
            case 'yellow':
                printer_yellow = self.env['ir.config_parameter'].sudo().get_param('ow_printnode.inspection_label_printer_yellow_id')
                self.printer_id = self.env['printnode.printer'].browse(int(printer_yellow))
    
    @api.depends("print_format")
    def _compute_avail_products_to_print(self):
        super()._compute_avail_products_to_print()
        for record in self:
            if record.move_ids:
                record.avail_products_to_print = record.move_ids.product_id.ids
            elif record.product_tmpl_line_ids:
                record.avail_products_to_print = record.product_tmpl_line_ids.product_tmpl_id.product_variant_ids.ids
            elif record.product_ids:
                record.avail_products_to_print = record.product_ids.ids
            else:
                record.avail_products_to_print = []
