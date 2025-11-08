# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.tools import float_compare


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'approval.button.mixin']
