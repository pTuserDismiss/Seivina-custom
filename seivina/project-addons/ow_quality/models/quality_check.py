# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _


class QualityCheck(models.Model):
    _inherit = 'quality.check'

    show_qt9_reminder = fields.Boolean(related='point_id.show_qt9_reminder', depends=['point_id'], store=True)

    def action_confirm_reupload_qt9(self):
        for record in self:
            record.message_post(body=_('Re-upload to QT9 confirmed'))
            record.show_qt9_reminder = False
