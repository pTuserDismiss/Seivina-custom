# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    taxjar_account_id = fields.Many2one('taxjar.account', 'TaxJar Account')

    @api.onchange('taxjar_account_id', 'country_id')
    def onchange_taxjar_account_id(self):
        for rec in self:
            if rec.taxjar_account_id:
                rec.auto_apply = True
                rec.country_id = rec.taxjar_account_id.mapped('state_ids') and rec.taxjar_account_id.mapped('state_ids')[0].country_id.id or False
                rec.state_ids = not rec.taxjar_account_id.is_calc_all_us_states and rec.taxjar_account_id.mapped('state_ids').ids or False

    @api.constrains('taxjar_account_id')
    def _validate_taxjar_account_country(self):
        for record in self:
            if record.taxjar_account_id and record.company_id.country_id and record.company_id.country_id.code != 'US':
                raise UserError(_("Please check your company country! \nFiscal positions are only supported with a TaxJar account when the company’s country is United States."))