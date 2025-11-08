from odoo import _, models


def _prepare_data(env, docids, data):
    products = []
    if data.get('products'):
        products = env['product.product'].browse(data.get('products'))
    return {
        'products': products,
        'po_no': data.get('po_no'),
        'supplier': data.get('supplier'),
        'receiving_date': data.get('receiving_date'),
    }


class ReportProductTemplateLabel2x7(models.AbstractModel):
    _name = 'report.ow_product.report_producttemplatelabel4x2p5'
    _description = 'Product Label Report 4x2.5'

    def _get_report_values(self, docids, data):
        return _prepare_data(self.env, docids, data)

class ReportProductLabelZplOw(models.AbstractModel):
    _name = 'report.ow_product.label_product_product_view_zpl_ow'
    _description = 'Product Label Report'

    def _get_report_values(self, docids, data):
        return _prepare_data(self.env, docids, data)
    