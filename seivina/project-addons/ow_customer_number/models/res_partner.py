# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    ref = fields.Char('Customer Number', tracking=True, readonly=False)

    @api.model_create_multi
    def create(self, vals_list):
        ref_values = {}
        for i, vals in enumerate(vals_list):
            if vals.get('ref'):
                ref_values[i] = vals['ref']
        
        res = super().create(vals_list)
        
        for i, record in enumerate(res):
            if i in ref_values:
                record.ref = ref_values[i]
            elif record.company_type == 'person':
                record.ref = ''
        
        return res
