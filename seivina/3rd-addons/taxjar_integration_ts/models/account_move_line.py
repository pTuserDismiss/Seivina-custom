from odoo import fields, models, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # Added for 'taxable tax amount' field to manually applied taxes
    # taxable_taxamount = fields.Float(compute="_compute_tax_ids", string='Taxable Taxes', help='Taxable Taxes for some categories. Writen temp taxes on this field.')
    # taxable_amount_ts = fields.Float(compute="_compute_tax_ids", string='Taxable Amount(TaxJar)',help='This field used when tax base amount less of actual subtotal. This field values come from TaxJar based on customer address and TaxJar product Category.')

    @api.onchange('quantity', 'discount','price_unit')
    def _apply_taxes_inline(self):
        for line in self:
            if line.display_type in ('line_section', 'line_note'):
                continue
            if line.product_id or line.account_id.tax_ids or not line.tax_ids:
                fpos = line.move_id.fiscal_position_id or False
                taxjar_account_id = fpos and fpos.taxjar_account_id or False
                partner_id = line.move_id.partner_id or False
                if line.product_id and line.price_unit and line.move_id.is_sale_document() and taxjar_account_id and partner_id and partner_id.state_id and partner_id.state_id in taxjar_account_id.state_ids and taxjar_account_id.state == 'confirm':
                    line._compute_inv_line_tax_id_from_taxjar(taxjar_account_id, line.move_id.partner_shipping_id)
                # else:
                #     line.taxable_taxamount = 0.0
                #     line.taxable_amount_ts = 0.0

    @api.depends('product_id', 'product_uom_id')
    def _compute_tax_ids(self):
        super(AccountMoveLine, self)._compute_tax_ids()
        for line in self:
            if line.display_type in ('line_section', 'line_note'):
                continue
            if line.product_id or line.account_id.tax_ids or not line.tax_ids:
                fpos = line.move_id.fiscal_position_id or False
                taxjar_account_id = fpos and fpos.taxjar_account_id or False
                partner_id = line.move_id.partner_id or False
                if line.product_id and line.price_unit and line.move_id.is_sale_document() and taxjar_account_id and partner_id and partner_id.state_id and partner_id.state_id in taxjar_account_id.state_ids and taxjar_account_id.state == 'confirm':
                    line._compute_inv_line_tax_id_from_taxjar(taxjar_account_id, line.move_id.partner_shipping_id)
                # else:
                #     line.taxable_taxamount = 0.0
                #     line.taxable_amount_ts = 0.0

    def convert_amount_in_usd(self, amount):
        usd_currency = self.env.ref('base.USD')
        date = self.move_id.date or self.move_id.invoice_date
        return self.currency_id._convert(amount, usd_currency, self.company_id, date)

    def get_taxjar_category(self):
        "Find categories for taxjar"
        taxjar_category_id = self.product_id and self.product_id.taxjar_category_id and self.product_id.taxjar_category_id or False
        if not taxjar_category_id:
            taxjar_category_id = self.product_id and self.product_id.categ_id and self.product_id.categ_id.taxjar_category_id or False
        return taxjar_category_id

    def _compute_inv_line_tax_id_from_taxjar(self,taxjar_account_id, shipping_partner):
        "Compute Invoices Line taxes"
        for rec in self:
            rec_partner = rec.move_id.company_id and rec.move_id.company_id.partner_id or False
            if rec.price_unit and rec_partner:
                taxjar_category = rec.get_taxjar_category() or self.env['taxjar.category']
                product_tax_code = taxjar_category and taxjar_category.product_tax_code or ''
                shipping_charge = 0.0 ##in the invoice line product we only able to select salling product(sale_ok).
                discount_amount = rec.discount and (rec.quantity * rec.price_unit) * rec.discount / 100 or 0.0
                line_dict = {
                    "amount": rec.price_subtotal or 0.0,
                    "shipping": shipping_charge,
                    "line_items": [
                        {
                            "quantity": rec.quantity,
                            "product_tax_code": product_tax_code,
                            "unit_price": rec.price_unit,
                            "discount": discount_amount
                        }
                    ]
                }
                is_delivery = rec.sale_line_ids and rec.sale_line_ids.filtered(lambda x:x.is_delivery) and True or False
                # is_delivery is False only when manully created invoice and not any sale line attached with invoice line.
                tax_ids, tax_amount, taxable_amount = taxjar_account_id.get_taxes(line_dict, taxjar_category, rec_partner, shipping_partner, is_delivery)
                rec.tax_ids = tax_ids
                # rec.write({'taxable_taxamount': tax_amount, 'taxable_amount_ts': taxable_amount})
                # rec.taxable_taxamount = taxable_amount
                # rec.taxable_amount_ts = tax_amount
                # return tax_ids, taxable_amount, tax_amount