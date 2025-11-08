# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields, Command, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    customer_deposit_journal_id = fields.Many2one('account.journal', string='Customer Deposit Journal')
    vendor_deposit_journal_id = fields.Many2one('account.journal', string='Vendor Deposit Journal')
    
    @api.model
    def init_account_deposit_data(self):
        self = self.sudo().with_context(active_test=False)
        
        # As the CoA is shared between child companies (branches), we just
        # initiate the accounting deposit data for Root Companies whose CoA
        # is already installed.
        root_companies = self.search([
            ('parent_id', '=', False),
            ('chart_template', '!=', False)
        ])
        root_companies.init_deposit_journals()
        root_companies.init_deposit_accounts()
        
    # -------------------------------------------------------------------------
    # account.journal
    # -------------------------------------------------------------------------
    
    def _prepare_customer_deposit_journal_vals(self):
        self.ensure_one()
        return {
            'type': 'general',
            'name': _('Customer Deposit'),
            'code': 'CDEP',
            'show_on_dashboard': False,
            'company_id': self.id,
        }
        
    def _prepare_vendor_deposit_journal_vals(self):
        self.ensure_one()
        return {
            'type': 'general',
            'name': _('Vendor Deposit'),
            'code': 'VDEP',
            'show_on_dashboard': False,
            'company_id': self.id,
        }

    @api.model
    def create_or_update_deposit_journal(self, field_name, meth_name):
        journal_env = self.env['account.journal']
        journal_vals = getattr(self, meth_name)()
        
        deposit_journal = journal_env.search([  
            ('type', '=', journal_vals['type']),
            ('code', '=', journal_vals['code']),
            ('company_id', '=', journal_vals['company_id']),
        ], limit=1)
        if not deposit_journal:
            deposit_journal = journal_env.create(journal_vals)
        
        self[field_name] = deposit_journal
        return deposit_journal
        
    def init_deposit_journals(self):
        for company in self:
            # Create journal records
            customer_deposit_journal = company.create_or_update_deposit_journal(
                field_name='customer_deposit_journal_id',
                meth_name='_prepare_customer_deposit_journal_vals'
            )
            vendor_deposit_journal = company.create_or_update_deposit_journal(
                field_name='vendor_deposit_journal_id',
                meth_name='_prepare_vendor_deposit_journal_vals'
            )
            
            # Create associated external id
            self.env['ir.model.data']._update_xmlids([{
                'xml_id': f'account.{company.id}_customer_deposit',
                'record': customer_deposit_journal,
                'noupdate': True,
            }])
            self.env['ir.model.data']._update_xmlids([{
                'xml_id': f'account.{company.id}_vendor_deposit',
                'record': vendor_deposit_journal,
                'noupdate': True,
            }])
            
    # -------------------------------------------------------------------------
    # account.account
    # -------------------------------------------------------------------------
    
    def _prepare_customer_deposit_account_vals(self):
        self.ensure_one()
        return {
            'code': '111400',
            'name': 'Customer Deposit',
            'account_type': 'liability_current',
            'reconcile': True,
            'company_ids': [Command.set(self.ids)],
        }
        
    def _prepare_vendor_deposit_account_vals(self):
        self.ensure_one()
        return {
            'code': '103000',
            'name': 'Prepayments',
            'account_type': 'asset_prepayments',
            'reconcile': True,
            'company_ids': [Command.set(self.ids)],
        }

    @api.model
    def create_or_update_deposit_account(self, meth_name):
        self.ensure_one()
        account_env = self.env['account.account']
        account_vals = getattr(self, meth_name)()
        
        deposit_account = account_env.search([
            ('code', '=', account_vals['code']),
            ('name', 'like', account_vals['name']),
            ('account_type', '=', account_vals['account_type']),
            ('company_ids', 'in', account_vals['company_ids'][0][2]),
        ], limit=1)
        if deposit_account:
            deposit_account.reconcile = True
        else:
            deposit_account = account_env.create(account_vals)
            
        return deposit_account
            
    def init_deposit_accounts(self):
        for company in self.filtered(lambda r: r.chart_template == 'generic_coa'):
            
            # Create or Update CoA
            customer_account = company.create_or_update_deposit_account(
                meth_name='_prepare_customer_deposit_account_vals'
            )
            vendor_account = company.create_or_update_deposit_account(
                meth_name='_prepare_vendor_deposit_account_vals'
            )
            
            # Create associated external id
            self.env['ir.model.data']._update_xmlids([{
                'xml_id': f'account.{company.id}_conf_customer_deposit',
                'record': customer_account,
                'noupdate': True,
            }])
            self.env['ir.model.data']._update_xmlids([{
                'xml_id': f'account.{company.id}_prepayments',
                'record': vendor_account,
                'noupdate': True,
            }])
            
            # Create or Update Company Properties
            company.create_or_update_deposit_property(
                field_name='property_account_customer_deposit_id',
                account=customer_account
            )
            company.create_or_update_deposit_property(
                field_name='property_account_vendor_deposit_id',
                account=vendor_account
            )
        
    # -------------------------------------------------------------------------
    # ir.property
    # -------------------------------------------------------------------------
    
    @api.model
    def create_or_update_deposit_property(self, field_name, account):
        if not account:
            return
        
        # CoA is shared between child companies, but Company Property is not
        companies = self | self.child_ids
        IrDefault = self.env['ir.default'].sudo()

        for child in companies:
            IrDefault.set(
                model_name='res.partner',
                field_name=field_name,
                value=account.id,
                user_id=False,
                company_id=child.id
            )
