
from lxml import etree
from psycopg2.extensions import AsIs

from odoo import api, fields, models
from odoo.exceptions import ValidationError

class TierValidation(models.AbstractModel):
    _inherit = "tier.validation"

    _cancel_state_to = ["canceled","cancel"]

    is_post_validation = fields.Boolean(compute="_compute_is_post_validation")
    is_cancel_validation = fields.Boolean(compute="_compute_is_cancel_validation")
    hide_cancel_button = fields.Boolean(compute='_compute_hide_buttons_in_validating', readonly=True)
    is_delete_validation = fields.Boolean(compute="_compute_is_delete_validation")
    post_approved = fields.Boolean(compute="_compute_approved")
    cancel_approved = fields.Boolean(compute="_compute_approved")
    delete_approved = fields.Boolean(compute="_compute_approved")
    require_cancel_approval = fields.Boolean(string="Require Cancel Approval")
    require_delete_approval = fields.Boolean(string="Require Delete Approval")

    @api.depends("review_ids.status")
    def _compute_approved(self):
        for rec in self:
            rec.post_approved = any(review.action_type == "post" and review.status in ["approved"] and review.requested_by == rec.env.user for review in rec.review_ids)
            rec.cancel_approved = any(review.action_type == "cancel" and review.status in ["approved"] and review.requested_by == rec.env.user for review in rec.review_ids)
            rec.delete_approved = any(review.action_type == "delete" and review.status in ["approved"] and review.requested_by == rec.env.user for review in rec.review_ids)


    @api.depends("need_validation")
    def _compute_hide_buttons_in_validating(self):
        for this in self:
            this.hide_cancel_button |= this.need_validation
            
    def _prepare_tier_review_vals(self, definition, sequence):
        res = super()._prepare_tier_review_vals(definition, sequence)
        if self.env.context.get("action_type"):
            if self.env.context.get("action_type") == "cancel":
                res["action_type"] = 'cancel'
            elif self.env.context.get("action_type") == "delete":
                res["action_type"] = 'delete'
        return res

    def request_cancel(self):
        self = self.with_context(action_type="cancel")
        return self.request_validation()
    
    def request_delete(self):
        self = self.with_context(action_type="delete")
        return self.request_validation()

    def restart_validation(self):
        super().restart_validation()
        # set back to default action type for future requests
        # self.write({'_approve_cancel': False})
        self = self.with_context(action_type="post")

    def _add_tier_validation_label(self, node, params):
        str_element = self.env["ir.qweb"]._render(
            "ow_base_tier_validation.tier_all_action_validation_label", params
        )
        new_node = etree.fromstring(str_element)
        return new_node
        
    def _compute_is_post_validation(self):
        for rec in self:
            rec.is_post_validation = any(review.action_type == "post" and review.status in ["waiting", "pending"] and (review.requested_by == rec.env.user or rec.env.user in review.reviewer_ids) for review in rec.review_ids)
    
    def _compute_is_cancel_validation(self):
        for rec in self:
            rec.is_cancel_validation = any(review.action_type == "cancel" and review.status in ["waiting", "pending"] and (review.requested_by == rec.env.user or rec.env.user in review.reviewer_ids) for review in rec.review_ids)

    def _compute_is_delete_validation(self):
        for rec in self:
            rec.is_delete_validation = any(review.action_type == "delete" and review.status != ["waiting", "pending"] and (review.requested_by == rec.env.user or rec.env.user in review.reviewer_ids) for review in rec.review_ids)

    def _check_state_conditions(self, vals):
        return (
            self._check_state_from_condition()
            and (vals.get(self._state_field) in self._state_to)
                 or (vals.get(self._state_field) in self._cancel_state_to)
        )
    
    def _tier_validation_check_state_on_write(self, vals):
        for rec in self:
            if rec._check_state_conditions(vals):
                if rec.review_ids:
                    if vals.get(self._state_field) in self._state_to and not rec.post_approved:
                        if rec.is_post_validation:
                            raise ValidationError(
                                self.env._(
                                    "This action is waiting for approval."
                                )
                            )
                        else:
                            raise ValidationError(
                                    self.env._(
                                        "This action needs approval. Please send request."
                                    )
                                )
                    elif vals.get(self._state_field) in self._cancel_state_to and not rec.cancel_approved:
                        if rec.is_cancel_validation:
                            raise ValidationError(
                                self.env._(
                                    "This action is waiting for approval."
                                )
                            )
                        else:
                            raise ValidationError(
                                    self.env._(
                                        "This action needs approval. Please send request."
                                    )
                                )
                else:
                    if rec.need_validation:
                        raise ValidationError(
                                self.env._(
                                    "This action needs approval. Please send request."
                                )
                            )

    def unlink(self):
        for rec in self:
            if rec.need_validation or not rec.is_delete_validation:
                raise ValidationError(
                        self.env._(
                           "This action needs approval. Please send request."
                        )
                    )
            if rec.review_ids and not rec.delete_approved:
                raise ValidationError(
                            self.env._(
                                "A validation process is still open or rejected for at least "
                                "one record. If you want to send new Validation request, please click Restart Validation."
                            )
                        )
        return super().unlink()
    
    @api.model
    def _get_validation_exceptions(self, extra_domain=None, add_base_exceptions=True):
        res = super()._get_validation_exceptions(extra_domain, add_base_exceptions)
        res.append("state")
        res.append("is_manually_modified")
        return res
