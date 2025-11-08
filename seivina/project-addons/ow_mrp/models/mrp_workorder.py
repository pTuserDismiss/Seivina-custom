# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import models, _
from odoo.exceptions import UserError


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    def button_start(self):
        if self.production_id._check_components_unavailable():
            raise UserError(_('Cannot start the WO. Some MOs are on hold due to insufficient components.'))
        return super().button_start()
