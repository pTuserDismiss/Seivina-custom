# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################

import logging

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class Website(models.Model):
    _inherit = "website"

    enforce_twofa_public = fields.Boolean(
        string="Enforce 2FA For Public User",
    )
    enforce_twofa_internal = fields.Boolean(
        string="Enforce 2FA For Internal User",
    )
