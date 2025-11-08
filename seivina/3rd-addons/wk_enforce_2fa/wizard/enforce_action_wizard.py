# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class EnforceTwoFAWizard(models.TransientModel):
    _name = 'enforce.twofa.wizard'
    _description = 'Enforce 2FA Wizard'

    user_ids = fields.Many2many(
        'res.users', 'res_users_enforce_2fa_rel',
        string='Users'
    )

    @api.model
    def default_get(self, fields):
        res = super(EnforceTwoFAWizard, self).default_get(fields)
        res_ids = self._context.get('active_ids')

        invoices = self.env['res.users'].browse(res_ids)
        if not invoices:
            raise UserError(_("Users are not selected"))

        res.update({
            'user_ids': res_ids,
        })
        return res

    def enforce_twofa_action(self):
        for rec in self.user_ids:
            rec.totp_enforced = True
