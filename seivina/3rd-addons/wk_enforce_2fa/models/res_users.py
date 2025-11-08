# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################

import base64
import io
import logging
import os
import werkzeug.urls

from odoo import _, api, fields, models
from odoo.addons.auth_totp.models.res_users import compress
from odoo.addons.auth_totp.models.totp import ALGORITHM, TOTP, TOTP_SECRET_SIZE, DIGITS, TIMESTEP
from odoo.http import request

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    totp_enforced = fields.Boolean(string="Enforce 2FA", default=False)
    totp_enforced_compute = fields.Boolean(
        string="Enforce 2FA ", compute="_totp_enforced_compute")

    def _totp_enforced_compute(self):
        website = self.env['website'].search(
            [('company_id', '=', self.env.company.id)], limit=1)
        for user in self:
            public = user.has_group('base.group_portal')
            if public and website.enforce_twofa_public and not user.totp_enabled:
                user.totp_enforced_compute = True
            elif not user.totp_enabled:
                user.totp_enforced_compute = user.totp_enforced
            else:
                user.totp_enforced_compute = False

    @api.model_create_multi
    def create(self, vals_list):
        users = super(ResUsers, self).create(vals_list)
        website = self.env['website'].get_current_website()
        for user in users:
            if user.has_group('base.group_user') and website.enforce_twofa_internal:
                user.totp_enforced = True
        return users

    # def write(self, values):
    #     res = super(ResUsers, self).write(values)
    #     website = self.env['website'].get_current_website()
    #     for user in self:
    #         if values.get('sel_groups_1_10_11',False) == 1 and website.enforce_twofa_internal:
    #             user.totp_enforced = True
    #     return res

    def generate_qrcode_tfa(self, web_login=False):
        if self.env.user != self and not web_login:
            return {
                'secret': False,
                'qr_code': False,
                'tfa_enabled': self.totp_enabled,
                'tfa_enforced': self.totp_enforced_compute,
            }

        if self.totp_enabled:
            return {
                'secret': False,
                'qr_code': False,
                'tfa_enabled': self.totp_enabled,
                'tfa_enforced': self.totp_enforced_compute,
            }

        secret_bytes_count = TOTP_SECRET_SIZE // 8
        secret = base64.b32encode(os.urandom(secret_bytes_count)).decode()
        # format secret in groups of 4 characters for readability
        secret = ' '.join(map(''.join, zip(*[iter(secret)]*4)))

        global_issuer = request and request.httprequest.host.split(':', 1)[0]
        issuer = global_issuer or self.company_id.display_name
        url = werkzeug.urls.url_unparse((
            'otpauth', 'totp',
            werkzeug.urls.url_quote(f'{issuer}:{self.login}', safe=':'),
            werkzeug.urls.url_encode({
                'secret': compress(secret),
                'issuer': issuer,
                # apparently a lowercase hash name is anathema to google
                # authenticator (error) and passlib (no token)
                'algorithm': ALGORITHM.upper(),
                'digits': DIGITS,
                'period': TIMESTEP,
            }), ''
        ))

        data = io.BytesIO()
        import qrcode
        qrcode.make(url.encode(), box_size=4).save(
            data, optimise=True, format='PNG')
        qr_code = base64.b64encode(data.getvalue()).decode()

        return {
            'secret': secret,
            'qr_code': qr_code,
            'tfa_enabled': self.totp_enabled,
            'tfa_enforced': self.totp_enforced_compute,
        }

    def _totp_try_setting_enforce(self, code, secret, web_login=False):
        if not web_login:
            if self.totp_enabled or self != self.env.user:
                _logger.info("2FA enable: REJECT for %s %r", self, self.login)
                return False

        secret = compress(secret).upper()
        match = TOTP(base64.b32decode(secret)).match(code)
        if match is None:
            _logger.info("2FA enable: REJECT CODE for %s %r", self, self.login)
            raise ValueError

        self.sudo().totp_secret = secret
        if request:
            self.env.flush_all()
            # update session token so the user does not get logged out (cache cleared by change)
            new_token = self.env.user._compute_session_token(
                request.session.sid)
            request.session.session_token = new_token

        _logger.info("2FA enable: SUCCESS for %s %r", self, self.login)
        return True

    def enable(self, code, secret):
        try:
            c = int(compress(str(code)))
        except ValueError:
            return {'success': False, 'error': _("The verification code should only contain numbers")}
        if self._totp_try_setting(secret, c):
            return {'success': True, 'error': _('Success: Two-factor authentication is now enabled.')}
        return {'success': False, 'error': _('Verification failed, please double-check the 6-digit verification code')}

    def tfa_check(self, code):
        try:
            self._totp_check(code)
        except:
            _logger.info("2FA check: FAIL for %s %r", self, self.login)
            return {
                'success': False,
                'error': _("2FA check FAIL, wrong verification code entered.")
            }
        _logger.info("2FA check: SUCCESS for %s %r", self, self.login)
        return {
            'success': True,
            'error': _("2FA check SUCCESS.")
        }

    def action_setup_enforce_2fa(self):
        return {
            'name': _("Enforce 2FA to Users"),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'enforce.twofa.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def _mfa_type(self):
        r = super()._mfa_type()
        if r is not None:
            return r
        if r == 'totp':
            return r
        if self.totp_enforced_compute:
            return 'enforce_totp'

    def _mfa_url(self):
        r = super()._mfa_url()
        if self._mfa_type() == 'enforce_totp':
            return '/web/login/totp/enforce'
        return r

    def action_totp_enforced(self):
        self.totp_enforced = not self.totp_enforced


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        result = super().session_info()
        return self._add_custom_enforce_session_info(result)

    def get_frontend_session_info(self):
        result = super().get_frontend_session_info()
        return self._add_custom_enforce_session_info(result)

    def _add_custom_enforce_session_info(self, session_info):
        session_info['tfa_enforced'] = self.env.user.totp_enforced_compute
        session_info['tfa_enabled'] = self.env.user.totp_enabled
        return session_info
