from odoo import api, models, fields
from odoo.exceptions import UserError


class TierDefinition(models.Model):
    _inherit = "tier.definition"

    additional_conditions = fields.Selection(
        [
            ("total_amount_spent_over_period_of_time", "Total Amount Spent Over Period Of Time"),
        ],
        string="Additional Conditions"
    )
    amount = fields.Float(string='Amount')
    period = fields.Integer(string='Period')

    @api.onchange('model_id')
    def _onchange_model_id(self):
        for rec in self:
            if rec.model_id.model == "purchase.order":
                rec.additional_conditions = "total_amount_spent_over_period_of_time"
            else:
                rec.additional_conditions = None

    @api.onchange('additional_conditions')
    def _onchange_additional_conditions(self):
        for rec in self:
            if rec.additional_conditions == "total_amount_spent_over_period_of_time" and rec.model_id.model != "purchase.order":
                raise UserError("This option is not supported for the selected model.")
