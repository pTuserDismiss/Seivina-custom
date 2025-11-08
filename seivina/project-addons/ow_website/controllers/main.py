# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

import logging
_logger = logging.getLogger(__name__)

from odoo import http, _
from odoo.http import request
from odoo.exceptions import ValidationError
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleRequestQuote(WebsiteSale):
    """Extend WebsiteSale to handle Request Quote functionality."""

    @http.route(['/shop/request_quote'], type='http', auth="public", website=True, methods=['POST'], csrf=True)
    def request_quote(self, **post):
        try:
            order = request.website.sale_get_order()
            if not order or not order.website_order_line:
                return request.redirect('/shop/cart')

            customer_name = post.get('customer_name', '').strip()
            customer_email = post.get('customer_email', '').strip()
            customer_phone = post.get('customer_phone', '').strip()
            customer_address = post.get('customer_address', '').strip()
            quote_message = post.get('quote_message', '').strip()

            if not all([customer_name, customer_email, customer_phone, customer_address]):
                raise ValidationError(_("All required fields must be filled."))

            partner = request.env['res.partner'].sudo().search([
                ('email', '=', customer_email)
            ], limit=1)

            if not partner:
                partner = request.env['res.partner'].sudo().create({
                    'name': customer_name,
                    'email': customer_email,
                    'phone': customer_phone,
                    'street': customer_address,
                    'is_company': True,
                    'customer_rank': 1,
                })
                _logger.info(f"Created new contact: {partner.name} ({partner.email})")

            order.write({
                'partner_id': partner.id,
                'partner_invoice_id': partner.id,
                'partner_shipping_id': partner.id,
                'quote_message': quote_message,
            })
            
            request.session['quote_request_success'] = True
            return request.redirect('/shop/cart')

        except ValidationError as e:
            request.session['quote_request_error'] = str(e)
            return request.redirect('/shop/cart')
        except Exception as e:
            _logger.error(f"Error processing quote request: {str(e)}")
            request.session['quote_request_error'] = _("An error occurred while processing your request. Please try again.")
            return request.redirect('/shop/cart')

    @http.route(['/shop/cart'], type='http', auth="public", website=True, sitemap=False)
    def cart(self, access_token=None, revive='', **post):
        response = super().cart(access_token=access_token, revive=revive, **post)
        
        if request.session.get('quote_request_success'):
            request.session.pop('quote_request_success')
            response.qcontext['quote_success_message'] = _("Your quote request has been submitted successfully! Our sales team will contact you soon.")
        
        if request.session.get('quote_request_error'):
            request.session.pop('quote_request_error')
            response.qcontext['quote_error_message'] = request.session.get('quote_request_error')
        
        return response
