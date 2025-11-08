# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################

import re
import logging

from odoo import http, _
from odoo.exceptions import AccessDenied
from odoo.http import request
from odoo.addons.web.controllers import home as web_home
from odoo.addons.website_sale.controllers.main import WebsiteSale

_logger = logging.getLogger(__name__)


class Home(web_home.Home):

    @http.route(
        '/web/login/totp/enforce',
        type='http', auth='public', methods=['GET', 'POST'], sitemap=False,
        website=True, multilang=False  # website breaks the login layout...
    )
    def web_totp_enforce(self, redirect=None, **kwargs):
        if request.session.uid:
            return request.redirect(self._login_redirect(request.session.uid, redirect=redirect))

        if not request.session.pre_uid:
            return request.redirect('/web/login')

        error = None

        user = request.env['res.users'].browse(request.session.pre_uid)

        if user and request.httprequest.method == 'GET':
            enforce_vals = user.sudo().generate_qrcode_tfa(web_login=True)
            return request.render('wk_enforce_2fa.enforce_twofa', {
                'user': user,
                'error': error,
                'redirect': redirect,
                'secret': enforce_vals.get('secret'),
                'qr_code': enforce_vals.get('qr_code'),
                'tfa_enabled': enforce_vals.get('tfa_enabled'),
                'tfa_enforced': enforce_vals.get('tfa_enforced'),
            })

        elif user and request.httprequest.method == 'POST' and kwargs.get('code'):
            try:
                user.sudo()._totp_try_setting_enforce(
                    int(re.sub(r'\s', '', kwargs['code'])), kwargs['secret'], web_login=True)
            except AccessDenied as e:
                error = str(e)
            except ValueError:
                error = _("Invalid authentication code format.")
            else:
                request.session.finalize(request.env)
                request.update_env(user=request.session.uid)
                request.update_context(**request.session.context)
                response = request.redirect(self._login_redirect(
                    request.session.uid, redirect=redirect))
                # Crapy workaround for unupdatable Odoo Mobile App iOS (Thanks Apple :@)
                request.session.touch()
                return response

        # Crapy workaround for unupdatable Odoo Mobile App iOS (Thanks Apple :@)
        request.session.touch()
        enforce_vals = user.sudo().generate_qrcode_tfa(web_login=True)
        return request.render('wk_enforce_2fa.enforce_twofa', {
            'user': user,
            'error': error,
            'redirect': redirect,
            'secret': enforce_vals.get('secret'),
            'qr_code': enforce_vals.get('qr_code'),
            'tfa_enabled': enforce_vals.get('tfa_enabled'),
            'tfa_enforced': enforce_vals.get('tfa_enforced'),
        })


class WebsiteSale(WebsiteSale):

    @http.route()
    def shop_checkout(self, try_skip_step=None, **query_params):
        if request.env.user.totp_enforced_compute:
            return request.redirect('/shop/cart')
        return super(WebsiteSale, self).shop_checkout(try_skip_step, **query_params)
