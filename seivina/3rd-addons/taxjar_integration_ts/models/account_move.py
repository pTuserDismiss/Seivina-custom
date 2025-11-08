from odoo import models, _, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_sync_with_taxjar = fields.Boolean('Is sync with TaxJar', copy=False)

    @api.onchange('fiscal_position_id', 'partner_id')
    def onchange_fiscal_position_id_partner_id_ts(self):
        """
        Trigger the recompute of the taxes if the fiscal position is changed on the Invoice.
        """
        """Todo : Need to add warning when customer have not applied taxes"""
        for inv in self.filtered(lambda x : x.partner_id and x.is_sale_document()):
            inv.invoice_line_ids._compute_tax_ids()

    def convert_amount_in_usd(self, amount):
        usd_currency = self.env.ref('base.USD')
        date = self.date or self.invoice_date
        return self.currency_id._convert(amount, usd_currency, self.company_id, date)

    def export_transaction_to_taxjar(self):
        for invoice in self:
            line_items, shipping_price, amount_untaxed_ex, downpayment_amount = invoice.get_line_items()
            if not line_items:
                continue
            req_data = {
                'transaction_id': invoice.id,
                'transaction_date': str(invoice.invoice_date) or '',
            }
            taxjar_acc_id = invoice.fiscal_position_id.taxjar_account_id
            if (invoice.partner_shipping_id.state_id in taxjar_acc_id.state_ids) or (invoice.partner_shipping_id.country_code == 'US' and taxjar_acc_id.is_calc_all_us_states):
                req_data.update(taxjar_acc_id.get_from_address(invoice.company_id.partner_id))
                req_data.update(taxjar_acc_id.get_to_address(invoice.partner_shipping_id))

                sign = invoice.move_type in ['in_refund', 'out_refund'] and -1 or 1
                amount_untaxed = invoice.amount_untaxed + downpayment_amount
                amount_untaxed = amount_untaxed * sign
                amount_tax = (invoice.amount_tax * sign)
                # amount_tax = in_total_tax * sign

                usd_currency = self.env.ref('base.USD')
                if invoice.currency_id and invoice.currency_id != usd_currency:
                    # vals={'price_unit':price_unit,'discount_amount':discount_amount,'price_tax':price_tax}
                    amount_untaxed = invoice.convert_amount_in_usd(amount_untaxed)
                    amount_tax = invoice.convert_amount_in_usd(amount_tax)
                    if amount_untaxed_ex != amount_untaxed:
                        amount_untaxed = amount_untaxed_ex

                req_data.update({
                    'amount': amount_untaxed or 0.0,
                    'shipping': shipping_price,
                    'sales_tax': amount_tax or 0.0,
                    'line_items': line_items,
                })
                if invoice.move_type == 'out_invoice':
                    order_res = taxjar_acc_id._send_request('transactions/orders', json_data=req_data, method='POST')
                    body_message = 'Invoice Created on TaxJar.'
                else:
                    req_data.update({'transaction_reference_id': str(invoice.reversed_entry_id.id)})
                    order_res = taxjar_acc_id._send_request('transactions/refunds', json_data=req_data, method='POST')
                    body_message = 'Refund Invoice Created on TaxJar.'
                invoice.is_sync_with_taxjar = True
                invoice.message_post(body=_(body_message))
                self._cr.commit()
        return self

    def action_post(self):
        res = super(AccountMove, self).action_post()
        out_invoice_ids = self.filtered(lambda x : x.is_sale_document() and x.fiscal_position_id and x.fiscal_position_id.taxjar_account_id and x.fiscal_position_id.taxjar_account_id.transaction_sync and x.fiscal_position_id.taxjar_account_id.state == 'confirm')
        out_invoice_ids and out_invoice_ids.export_transaction_to_taxjar()
        return res

    def calculate_discount_amount(self,line,invoice_discount):
        discount_amount = line.discount and round((line.quantity * line.price_unit) * line.discount / 100,2) or 0.0
        price_total = line.price_subtotal
        # if discount_amount:
            # price_total -= discount_amount
        if invoice_discount:
            if invoice_discount > price_total:
                invoice_discount = round(invoice_discount - price_total,2)
                discount_amount = round(discount_amount + price_total,2)
            else:
                discount_amount = round(discount_amount + invoice_discount,2)
                invoice_discount = 0
        return discount_amount,invoice_discount

    def get_line_items(self):
        shipping_price = 0
        line_items = []
        amount_untaxed = 0.0
        downpayment_amount = 0.0

        lines = self.invoice_line_ids.filtered(lambda x: x.display_type not in ('line_section', 'line_note'))
        invoice_lines = lines.filtered(lambda x: x.price_unit >= 0)
        discount_lines = lines.filtered(lambda x : x.price_unit < 0)
        #invoice_discount = abs(sum(discount_lines.mapped('price_total')))
        invoice_discount = abs(sum(discount_lines.mapped('price_subtotal')))
        # discount_lines.price_subtotal

        for line in invoice_lines:
            usd_currency = self.env.ref('base.USD')
            sign = line.move_id.move_type in ['in_refund', 'out_refund'] and -1 or 1

            is_downpayment = line.sale_line_ids.filtered(lambda x: x.is_downpayment)
            if is_downpayment:
                downpayment_amount += line.price_unit * sign
                invoice_discount -= line.tax_base_amount
                continue
            refund_inv_id = line.move_id and line.move_id.reversed_entry_id or False
            if refund_inv_id:
                refund_line = refund_inv_id.invoice_line_ids.filtered(lambda x: x.product_id == line.product_id)
                # shipping_sale_line = refund_line.sale_line_ids.filtered(lambda sale_line:sale_line.is_delivery)
                shipping_sale_line = refund_line.mapped('sale_line_ids').filtered(lambda sale_line: sale_line.is_delivery)
            else:
                shipping_sale_line = line.sale_line_ids.filtered(lambda sale_line:sale_line.is_delivery)
            #Shipping : added discount condition when applied total order discount so it will also applied discount in the shipping line.
            if shipping_sale_line:
                if invoice_discount:
                    discount_amount, invoice_discount = self.calculate_discount_amount(line, invoice_discount)
                    shipping_price += round(line.price_subtotal - discount_amount,2)
                else:
                    shipping_price += line.price_subtotal
                shipping_price = line.move_id.currency_id and line.move_id.currency_id != usd_currency and line.convert_amount_in_usd(shipping_price) or shipping_price
                continue

            discount_amount, invoice_discount = self.calculate_discount_amount(line, invoice_discount)
            line_discount_price_unit = round(line.price_unit * (1 - (line.discount / 100.0)),2) if discount_amount else line.price_unit
            taxes_data = line.tax_ids and line.tax_ids.compute_all(
                line_discount_price_unit, currency=line.company_currency_id,quantity=line.quantity,product=line.product_id, partner=line.partner_id) or {}
            without_tax_amount = taxes_data.get('total_excluded', 0.0)
            with_tax_amount = taxes_data.get('total_included', 0.0)
            total_tax = with_tax_amount - without_tax_amount
            total_tax = round(total_tax,2)
            #discount_amount,invoice_discount = self.calculate_discount_amount(line,invoice_discount)
            # discount_amount = line.discount and (line.quantity * line.price_unit) * line.discount / 100 or 0.0
            price_unit = line.price_unit

            if line.move_id.currency_id and line.move_id.currency_id != usd_currency:
                price_unit = line.convert_amount_in_usd(price_unit)
                discount_amount = line.convert_amount_in_usd(discount_amount)
                total_tax = line.convert_amount_in_usd(total_tax)
                amount_untaxed += (price_unit * line.quantity) - discount_amount

            taxjar_category = line.get_taxjar_category() or self.env['taxjar.category']
            product_tax_code = taxjar_category and taxjar_category.product_tax_code or ''

            vals = {
                'quantity': line.quantity,
                'product_identifier': line.product_id and line.product_id.default_code or '',
                'product_tax_code': product_tax_code,
                'description': line.product_id and line.product_id.display_name or '',
                'unit_price': price_unit * sign,
                'discount':  0.0 if discount_amount == 0.0 else discount_amount * sign,
                'sales_tax': 0.0 if total_tax == 0.0 else total_tax * sign,
            }
            line_items.append(vals)
        return line_items, shipping_price, amount_untaxed, downpayment_amount

    def button_draft(self):
        out_invoice_ids = self.filtered(lambda x: x.is_sale_document() and x.is_sync_with_taxjar and x.fiscal_position_id and x.fiscal_position_id.taxjar_account_id and x.fiscal_position_id.taxjar_account_id.transaction_sync and x.fiscal_position_id.taxjar_account_id.state == 'confirm')
        res = super(AccountMove, self).button_draft()
        for invoice in out_invoice_ids.filtered(lambda x : x.is_sync_with_taxjar):
            taxjar_acc_id = invoice.fiscal_position_id.taxjar_account_id
            #commented it will only checking with Is_sync_with_taxjar boolean.
            #if invoice.partner_shipping_id.state_id in taxjar_acc_id.state_ids:
            if invoice.move_type == 'out_invoice':
                order_res = taxjar_acc_id._send_request('transactions/orders/' + str(invoice.id), method='DELETE')
                body_message = 'Invoice Removed on TaxJar.'
            else:
                order_res = taxjar_acc_id._send_request('transactions/refunds/' + str(invoice.id), method='DELETE')
                body_message = 'Refund Invoice Removed on TaxJar.'
            invoice.is_sync_with_taxjar = False
            invoice.message_post(body=_(body_message))
        return res
