from odoo import _, api, models, fields


class AccountPayment(models.Model):
    _name = "account.payment"
    _inherit = ["account.payment", "tier.validation"]
    _state_from = ["draft"]
    _state_to = ["in_process"]

    _tier_validation_manual_config = False

    hide_post_button = fields.Boolean(compute='_compute_hide_post_button', readonly=True)

    @api.depends("need_validation")
    def _compute_hide_post_button(self):
        for this in self:
            this.hide_post_button |= this.need_validation

    def _get_under_validation_exceptions(self):
        return super()._get_under_validation_exceptions() + ["needed_terms_dirty"]

    def _get_validation_exceptions(self, extra_domain=None, add_base_exceptions=True):
        res = super()._get_validation_exceptions(extra_domain, add_base_exceptions)
        # we need to exclude amount_total,
        # otherwise editing manually the values on lines dirties the field at onchange
        # since it's not in readonly because readonly="not(review_ids)", it's then
        # sent at save, and will override the values set by the user
        # return res + ["amount_total"]
        return res

    def _get_to_validate_message_name(self):
        name = super()._get_to_validate_message_name()
        if self.payment_type == "outbound":
            name = _("Send")
        elif self.payment_type == "inbound":
            name = _("Receive")
        return name

    def action_post(self):
        return super(
            AccountPayment, self.with_context(skip_validation_check=True)
        ).action_post()

    @api.model_create_multi
    def create(self, vals_list):
        for val in vals_list:
            val.update({"require_cancel_approval": True, "require_delete_approval": True})
        return super().create(vals_list)
    
    def _compute_need_validation(self):
        super()._compute_need_validation()
        for rec in self.filtered("need_validation"):
            if rec.sale_deposit_id:
                rec.need_validation = False