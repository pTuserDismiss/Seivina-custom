from odoo import fields, api, models
from odoo.tools.misc import formatLang

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('partner_shipping_id', 'partner_id', 'company_id')
    def _compute_fiscal_position_id(self):
        """Update taxes when shipping partner is changed"""
        super(SaleOrder, self)._compute_fiscal_position_id()
        for order in self:
            if order.fiscal_position_id:
                taxjar_acc_id = order.fiscal_position_id and order.fiscal_position_id.taxjar_account_id or False
                if taxjar_acc_id and taxjar_acc_id.state == 'confirm':
                    order.order_line._compute_tax_id_from_taxjar(taxjar_acc_id, order.partner_shipping_id)
                else:
                    order.order_line._compute_tax_id()

    @api.onchange('fiscal_position_id')
    def _onchange_fpos_id_show_update_fpos(self):
        """
        Trigger the recompute of the taxes if the fiscal position is changed on the SO.
        """
        res = super(SaleOrder, self)._onchange_fpos_id_show_update_fpos()
        for order in self:
            taxjar_account_id = order.fiscal_position_id.taxjar_account_id
            if taxjar_account_id and taxjar_account_id.state == 'confirm':
                order.order_line._compute_tax_id_from_taxjar(taxjar_account_id, order.partner_shipping_id)
            else:
                order.order_line._compute_tax_id()
        return res

    @api.onchange('warehouse_id')
    def _onchange_warehouse_id(self):
        for order in self:
            taxjar_account_id = order.fiscal_position_id.taxjar_account_id
            if taxjar_account_id and taxjar_account_id.state == 'confirm':
                order.order_line._compute_tax_id_from_taxjar(taxjar_account_id, order.partner_shipping_id)

    def _create_delivery_line(self, carrier, price_unit):
        sol = super(SaleOrder, self)._create_delivery_line(carrier, price_unit)
        self.mapped('order_line').mapped('tax_id') and sol._compute_tax_id()
        return sol


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    taxable_taxamount = fields.Float('Taxable Taxes',
                                     help='Taxable Taxes for some categories. Writen temp taxes on this field. Get exact Taxes per line for specific category product.')
    taxable_amount_ts = fields.Float('Taxable Amount(TaxJar)',
                                     help='This field used when taxable amount less of actual subtotal. This field values come from TaxJar based on customer address and TaxJar product Category.')

    # def _prepare_invoice_line(self, **optional_values):
    #     ##modified for 'taxable taxamount' field to manually applied taxes
    #     res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
    #     res['taxable_taxamount'] = self.taxable_taxamount
    #     res['taxable_amount_ts'] = self.taxable_amount_ts
    #     return res

    def get_taxjar_category(self):
        taxjar_category_id = self.product_id and self.product_id.taxjar_category_id or False
        if not taxjar_category_id:
            taxjar_category_id = self.product_id and self.product_id.categ_id and self.product_id.categ_id.taxjar_category_id or False
        return taxjar_category_id

    @api.onchange('price_unit','discount','product_uom_qty')
    def onchange_price_and_qty(self):
        compute_taxes_line = self.filtered(
            lambda x: x.order_id.fiscal_position_id.taxjar_account_id.state == 'confirm' or x.order_id.partner_id.property_account_position_id.taxjar_account_id.state == 'confirm')
        for line in compute_taxes_line:
            fpos = line.order_id.fiscal_position_id or line.order_id.partner_id.property_account_position_id
            if fpos.taxjar_account_id and fpos.taxjar_account_id.state == 'confirm':
                line._compute_tax_id_from_taxjar(fpos.taxjar_account_id, line.order_id.partner_shipping_id)

    @api.depends('product_id')
    def _compute_tax_id(self):
        """Implement Taxjar Taxes while creating order line"""
        compute_taxes_line = self.filtered(
            lambda x: x.order_id.fiscal_position_id.taxjar_account_id.state == 'confirm' or x.order_id.partner_id.property_account_position_id.taxjar_account_id.state == 'confirm')
        no_taxes_line = self - compute_taxes_line
        for line in compute_taxes_line:
            fpos = line.order_id.fiscal_position_id or line.order_id.partner_id.property_account_position_id
            if fpos.taxjar_account_id and fpos.taxjar_account_id.state == 'confirm':
                line._compute_tax_id_from_taxjar(fpos.taxjar_account_id, line.order_id.partner_shipping_id)
        if no_taxes_line:
            return super(SaleOrderLine, no_taxes_line)._compute_tax_id()

    def _compute_tax_id_from_taxjar(self, taxjar_account_id, shipping_partner):
        for line in self:
            warehouse_partner = line.order_id.warehouse_id and line.order_id.warehouse_id.partner_id or False
            if line.price_unit and warehouse_partner:
                taxjar_category = line.get_taxjar_category() or self.env['taxjar.category']
                product_tax_code = taxjar_category and taxjar_category.product_tax_code or ''
                shipping_charge = line.is_delivery and line.price_subtotal or 0.0
                discount_amount = line.discount and (line.product_uom_qty * line.price_unit) * line.discount / 100 or 0.0
                line_dict = {
                    "amount": not shipping_charge and line.price_subtotal or 0.0,
                    "shipping": shipping_charge,
                    "line_items": [
                        {
                            "quantity": line.product_uom_qty,
                            "product_tax_code": product_tax_code,
                            "unit_price": not shipping_charge and line.price_unit or 0.0,
                            "discount": discount_amount
                        }
                    ]
                }
                tax_id, tax_amount, taxable_amount = taxjar_account_id.get_taxes(line_dict, taxjar_category, warehouse_partner, shipping_partner, line.is_delivery)
                line.tax_id = tax_id
                line.taxable_taxamount = tax_amount
                line.taxable_amount_ts = taxable_amount
