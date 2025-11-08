# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import models, _
from odoo.addons.account.models.chart_template import template


class AccountChartTemplate(models.AbstractModel):
    _inherit = 'account.chart.template'
    
    @template(template='generic_coa', model='account.journal')
    def _get_deposit_account_journal(self):
        company = self.env.company
        return {
            'customer_deposit': company._prepare_customer_deposit_journal_vals(),
            'vendor_deposit': company._prepare_vendor_deposit_journal_vals(),
        }
        
    @template(template='generic_coa', model='account.account')
    def _get_deposit_account_account(self):
        company = self.env.company
        return {
            'conf_customer_deposit': company._prepare_customer_deposit_account_vals(),
        }
        
    @template(template='generic_coa')
    def _get_deposit_template_data(self):
        return {
            'property_account_customer_deposit_id': 'conf_customer_deposit',
            'property_account_vendor_deposit_id': 'prepayments',
        }
        
    def _post_load_data(self, template_code, company, template_data):
        super()._post_load_data(template_code, company, template_data)
        company = company or self.env.company
        fields = [
            'property_account_customer_deposit_id',
            'property_account_vendor_deposit_id'
        ]
        for fname in fields:
            fname_xml = template_data.get(fname)
            if fname_xml:
                account = self.ref(fname_xml, raise_if_not_found=False)
                company.create_or_update_deposit_property(fname, account)
