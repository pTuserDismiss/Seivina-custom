from odoo import api, models


class TierValidation(models.AbstractModel):
    _inherit = "tier.validation"

    @api.model
    def _get_validation_exceptions(self, extra_domain=None, add_base_exceptions=True):
        """Extend for more field exceptions to be written after validation."""
        res = super()._get_validation_exceptions(extra_domain, add_base_exceptions)
        return res + [
            "needed_terms_dirty",
            "is_manually_modified",
            "matched_payment_ids",
        ]
