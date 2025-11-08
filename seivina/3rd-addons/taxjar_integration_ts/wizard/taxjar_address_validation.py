from odoo import fields, models


class TaxjarAddressValidation(models.TransientModel):
    _name = "taxjar.address.validation"
    _description = "Taxjar Address Validation"

    partner_id = fields.Many2one('res.partner', required=True)
    verified_street = fields.Char(string="Street")
    verified_city = fields.Char(string="City")
    verified_zip = fields.Char(string="Zip")
    verified_state_id = fields.Many2one('res.country.state', string="State")
    verified_country_id = fields.Many2one('res.country', string="Country")
    street = fields.Char(related='partner_id.street', string="Street")
    city = fields.Char(related='partner_id.city', string="City")
    zip = fields.Char(related='partner_id.zip', string="Zip")
    state_id = fields.Many2one('res.country.state', related='partner_id.state_id', string="State")
    country_id = fields.Many2one('res.country', related='partner_id.country_id', string="Country")
    taxjar_verified_address_ids = fields.One2many('taxjar.verified.address', 'taxjar_address_validation_id', string="Taxjar Verified Addresses")

    def action_save_verified_address(self):
        for wizard_id in self:
            address_vals = {
                'street': wizard_id.verified_street,
                'city': wizard_id.verified_city,
                'zip': wizard_id.verified_zip,
                'state_id': wizard_id.verified_state_id.id if wizard_id.verified_state_id else False,
                'country_id': wizard_id.verified_country_id.id if wizard_id.verified_country_id else False,
            }
            wizard_id.partner_id.write(address_vals)
        return True
