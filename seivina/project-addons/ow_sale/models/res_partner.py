from odoo import models, fields, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_customer_po_mandatory = fields.Boolean(string="Customer PO Required?",
                                              help="""If checked, this contact and all of their related contacts
                                              require Customer Reference set on their sales orders.""",
                                              search="_search_is_customer_po_mandatory")

    def _any_node_is_customer_po_mandatory(self):
        self.ensure_one()
        self = self.sudo()
        if self.is_customer_po_mandatory:
            return True
        if not self.parent_id or not self.parent_id.active:
            return False
        return self.parent_id._any_node_is_customer_po_mandatory()

    def _search_is_customer_po_mandatory(self, operator, value):
        if operator not in ['=', '!=']:
            raise ValueError(_('This operator is not supported'))
        if not isinstance(value, bool):
            raise ValueError(_('Value should be True or False (not %s)'), value)

        result_ids = set()
        contacts = self.env['res.partner'].sudo().search([
            ('company_id', 'in', [self.env.company.id, False]),
            ('active', '=', True)
        ])
        for contact in contacts:
            if contact._any_node_is_customer_po_mandatory():
                result_ids.add(contact.id)
        if (operator == '!=' and value) or (operator == '=' and not value):
            domain_operator = 'not in'
        else:
            domain_operator = 'in'
        return [('id', domain_operator, result_ids)]
