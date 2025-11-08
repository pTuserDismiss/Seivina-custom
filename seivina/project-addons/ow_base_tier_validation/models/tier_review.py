from odoo import api, fields, models
from odoo.exceptions import ValidationError

class TierReview(models.Model):
    _inherit = "tier.review"
    
    action_type = fields.Selection(
        [
            ("post", "Post"),
            ("cancel", "Cancel"),
            ("delete", "Delete")
        ],
        default="post",
    )
