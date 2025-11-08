# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class QualityCheckWizard(models.TransientModel):
    _inherit = 'quality.check.wizard'

    show_qt9_reminder = fields.Boolean(related='current_check_id.show_qt9_reminder')

    def action_confirm_reupload_qt9(self):
        self.current_check_id.action_confirm_reupload_qt9()
        return {
            'name': self.current_check_id._get_check_action_name(),
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': self._context,
            'type': 'ir.actions.act_window',
        }
