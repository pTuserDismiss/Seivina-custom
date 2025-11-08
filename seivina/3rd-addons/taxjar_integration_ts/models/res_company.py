from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    allow_address_validation_taxjar = fields.Boolean(string="Allow Address Validation with TaxJar")
