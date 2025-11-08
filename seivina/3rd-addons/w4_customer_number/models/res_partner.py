from odoo import models, fields, api, SUPERUSER_ID

class Customer(models.Model):
    _inherit = 'res.partner'

    ref = fields.Char('Customer Number', tracking=True,readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        config = self.env['ir.config_parameter'].get_param('w4_customer_number.generate_number_for_new_customers', False)
        if config:
            for vals in vals_list:
                if not vals.get('parent_id'):
                    vals['ref'] = self.env['ir.sequence'].next_by_code('res.partner') or _('New')
                elif vals.get('parent_id'):
                    vals['ref'] = self.env['res.partner'].browse(vals['parent_id']).ref
        return super().create(vals_list)

    def write(self, values):
        config = self.env['ir.config_parameter'].get_param('w4_customer_number.generate_number_for_new_customers', False)
        res = super(Customer, self).write(values)
        if config:
            if 'parent_id' in values:
                self.update_customer_number_ref()
            self._update_sub_contacts()
        return res
    
    def update_customer_number_ref(self):
        for rec in self:
            if rec.parent_id:
                rec.ref = rec.parent_id.ref
            else:
                rec.ref = self.env['ir.sequence'].next_by_code('res.partner')

    def _update_sub_contacts(self):
        for rec in self:
            sub_contacts = self.env['res.partner'].search([('parent_id', '=', rec.id)])
            sub_contacts.write({'ref':rec.ref})

    def cron_update_customer_number_ref(self):
        parent_contacts = self.env['res.partner'].search([('parent_id', '=', False), ('ref', '=', False)])
        for rec in parent_contacts:
            rec.ref = self.env['ir.sequence'].next_by_code('res.partner')
            sub_contacts = self.env['res.partner'].search([('parent_id', '=', rec.id)])
            sub_contacts.write({'ref':rec.ref})