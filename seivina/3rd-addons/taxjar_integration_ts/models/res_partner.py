from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    _get_ts_exemption_type = [('wholesale', 'Wholesales Or Resale Exempt'),
                              ('government', 'Government Entity Exempt'),
                              ('other', 'Entity Exempt'),
                              ('non_exempt', 'Not Exempt')]
    ts_exemption_type = fields.Selection(_get_ts_exemption_type, default='non_exempt', string='TaxJar Exempt Type',
                                         help='This values used while calculating order taxes and invoice upload to TaxJar for this partner.')
    show_taxjar_address_validation = fields.Boolean(compute='_compute_show_taxjar_address_validation', string='Show TaxJar Address Validation')

    @api.depends('street', 'city', 'zip', 'state_id', 'country_id')
    def _compute_show_taxjar_address_validation(self):
        for partner in self:
            company = partner.company_id or self.env.company
            has_address = any([partner.street, partner.city, partner.state_id, partner.zip])
            if company.allow_address_validation_taxjar and has_address and partner.country_code == 'US':
                partner.show_taxjar_address_validation = True
            else:
                partner.show_taxjar_address_validation = False

    def action_open_taxjar_address_validation_wizard(self):
        for partner in self:
            company = partner.company_id or self.env.company
            taxjar_acc_id = self.env['taxjar.account'].search([('company_id', '=', company.id), ('state', '=', 'confirm')])

            if not taxjar_acc_id:
                raise ValidationError(_("Taxjar account not found or not confirmed."))

            req_data = self._prepare_request_data(partner)

            response = taxjar_acc_id._send_request('addresses/validate', json_data=req_data, method='POST')
            verified_addresses = response.get('addresses')

            if verified_addresses:
                wizard_id = self._create_taxjar_validation_wizard(partner, verified_addresses)
                return self._get_action_view(wizard_id)

        return True

    def _prepare_request_data(self, partner):
        fields = ['street', 'city', 'zip', 'state_id', 'country_id']
        req_data = {field: getattr(partner, field) for field in fields if getattr(partner, field)}

        if 'state_id' in req_data:
            req_data['state'] = req_data.pop('state_id').code
        if 'country_id' in req_data:
            req_data['country'] = req_data.pop('country_id').code

        return req_data

    def _create_taxjar_validation_wizard(self, partner, verified_addresses):
        taxjar_address_validation_vals = {'partner_id': partner.id}

        if len(verified_addresses) > 1:
            verified_address_list = self._prepare_validated_address_list(verified_addresses)
            taxjar_address_validation_vals.update({'taxjar_verified_address_ids': verified_address_list})
        elif verified_addresses:
            verified_address = verified_addresses[0]
            verified_address_vals = self._prepare_single_validated_address(verified_address)
            taxjar_address_validation_vals.update(verified_address_vals)

        return self.env['taxjar.address.validation'].create(taxjar_address_validation_vals)

    def get_state_and_country(self, address):
        state_code = address.get('state', '')
        country_code = address.get('country', '')
        country_id = self.env['res.country'].search([('code', '=', country_code)])
        state_id = self.env['res.country.state'].search([('code', '=', state_code), ('country_id', '=', country_id.id)])
        return state_id, country_id

    def _prepare_validated_address_list(self, verified_addresses):
        verified_address_list = []
        for address in verified_addresses:
            state_id, country_id = self.get_state_and_country(address)
            verified_address_list.append((0, 0, {
                "street": address.get('street', ''),
                "city": address.get('city', ''),
                "zip": address.get('zip', ''),
                "state_id": state_id.id if state_id else False,
                "country_id": country_id.id if country_id else False,
            }))
        return verified_address_list

    def _prepare_single_validated_address(self, verified_address):
        state_id, country_id = self.get_state_and_country(verified_address)
        verified_address_vals = {
            "verified_street": verified_address.get('street', ''),
            "verified_city": verified_address.get('city', ''),
            "verified_zip": verified_address.get('zip', ''),
            "verified_state_id": state_id.id if state_id else False,
            "verified_country_id": country_id.id if country_id else False,
        }
        return verified_address_vals

    def _get_action_view(self, wizard_id):
        if wizard_id.taxjar_verified_address_ids:
            view_id = self.env.ref("taxjar_integration_ts.taxjar_address_validation_view_form_2", False).id
            view_name = _('TaxJar Verified Addresses')
        else:
            view_id = self.env.ref("taxjar_integration_ts.taxjar_address_validation_view_form_1", False).id
            view_name = _('TaxJar Verified Address')

        return {
            'name': view_name,
            'type': 'ir.actions.act_window',
            'res_model': 'taxjar.address.validation',
            'view_id': view_id,
            'view_mode': 'form',
            'res_id': wizard_id.id,
            'target': 'new',
        }
