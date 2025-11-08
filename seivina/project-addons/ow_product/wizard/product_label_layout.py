from collections import defaultdict
from odoo import fields, models, api


class ProductLabelLayout(models.TransientModel):
    _inherit = 'product.label.layout'

    product_to_print_id = fields.Many2one('product.product', string='Product To Print')
    inspection_label_warning = fields.Char("Inspection Label Warning", compute="_compute_inspection_label_warning")
    avail_products_to_print = fields.Many2many(
        comodel_name='product.product',
        string='Available Products To Print',
        compute='_compute_avail_products_to_print'
    )
    print_format = fields.Selection(selection_add=[
        ('4x2.5', '4 x 2.5')
    ], default='4x2.5', ondelete={'4x2.5': 'set default'})

    @api.depends("product_to_print_id")
    def _compute_inspection_label_warning(self):
        if self.product_to_print_id:
            warning_dict = {"yellow": "Product marked for Inspection - Print on Yellow label",
                            "blue": "Product marked as Medical - Print on Blue label",
                            "white": "Print on White label" }
            self.inspection_label_warning = warning_dict.get(self.product_to_print_id.inspection_label,"")
        else:
            self.inspection_label_warning = ""


    @api.depends("print_format")
    def _compute_avail_products_to_print(self):
        if self.move_ids:
            self.avail_products_to_print = self.move_ids.product_id.ids

    def _prepare_report_data(self):
        xml_id, data = super()._prepare_report_data()
        if self.print_format == 'zpl':
            xml_id = 'ow_product.label_product_product_zpl_ow'
        elif self.print_format == '4x2.5':
            xml_id = 'ow_product.report_product_template_label_4x2p5'
        products = []
        if self.product_to_print_id:
            products.append(self.product_to_print_id.id)
        elif self.move_ids:
                products = self.move_ids.product_id.ids
        data['products'] = products
        if self.move_ids:
            po = self.env['purchase.order']
            if self.move_ids[0].purchase_line_id:
                po = self.move_ids[0].purchase_line_id.order_id
            elif self.move_ids[0].origin:
                po = self.env['purchase.order'].search([('name','=',self.move_ids[0].origin)])
            if po:
                data['supplier'] = po.partner_id.name
                data['po_no'] = po.name
                data['receiving_date'] = po.effective_date.strftime('%m/%d/%Y') if po.effective_date else ''
            else:
                data['supplier'] = ''
                data['po_no'] = ''
                data['receiving_date'] = ''
        else:
            data['supplier'] = ''
            data['po_no'] = ''
            data['receiving_date'] = ''
        return xml_id, data
