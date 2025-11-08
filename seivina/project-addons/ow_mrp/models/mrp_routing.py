from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    @api.constrains('time_cycle_manual')
    def _check_time_cycle_manual_is_positive(self):
        records = self.filtered(lambda r: r.time_cycle_manual <= 0)
        if records:
            raise ValidationError(_("The Default Duration must be greater than 0."))
