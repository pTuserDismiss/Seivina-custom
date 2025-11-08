from odoo import fields, models


class TaxjarVerifiedAddress(models.TransientModel):
    _name = "taxjar.verified.address"
    _description = "Taxjar Verified Address"

    taxjar_address_validation_id = fields.Many2one('taxjar.address.validation')
    street = fields.Char(string="Street")
    city = fields.Char(string="City")
    zip = fields.Char(string="Zip Code")
    state_id = fields.Many2one('res.country.state', string="State")
    country_id = fields.Many2one('res.country', string="Country")

    def action_save_verified_address(self):
        for verified_address in self:
            address_vals = {
                'street': verified_address.street,
                'city': verified_address.city,
                'zip': verified_address.zip,
                'state_id': verified_address.state_id.id if verified_address.state_id else False,
                'country_id': verified_address.country_id.id if verified_address.country_id else False,
            }
            verified_address.taxjar_address_validation_id.partner_id.write(address_vals)
        return True
