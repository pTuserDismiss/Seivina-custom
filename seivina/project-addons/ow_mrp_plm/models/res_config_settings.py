from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    prevent_bom_create_edit = fields.Boolean(
        string='Prevent create/edit BOM',
        config_parameter='ow_mrp_plm.prevent_bom_create_edit',
        default=False,
    )
