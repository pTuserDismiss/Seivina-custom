# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################

from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enforce_twofa_public = fields.Boolean(
        string="Enforce 2FA For Public User",
        related="website_id.enforce_twofa_public",
        readonly=False
    )
    enforce_twofa_internal = fields.Boolean(
        string="Enforce 2FA For Internal User",
        related="website_id.enforce_twofa_internal",
        readonly=False
    )
