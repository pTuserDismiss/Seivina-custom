from odoo import api, models, fields, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_customer_po_mandatory = fields.Boolean(string="Customer PO Required?",
                                              help="This is populated from the customer by default. The user could override")
    user_has_group_sales_admin = fields.Boolean(compute='_compute_user_has_group_validate_bank_account')

    @api.depends_context('uid')
    def _compute_user_has_group_validate_bank_account(self):
        user_has_group_sales_admin = self.env.user.has_group('sales_team.group_sale_manager')
        for rec in self:
            rec.user_has_group_sales_admin = user_has_group_sales_admin

    @api.onchange('partner_id')
    def _onchange_partner_id_customer_po(self):
        if self._origin.id or not self.partner_id:
            return
        self.is_customer_po_mandatory = self.partner_id._any_node_is_customer_po_mandatory()

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if 'partner_id' in values:
                customer = self.env['res.partner'].browse(values['partner_id'])
                values['is_customer_po_mandatory'] = customer._any_node_is_customer_po_mandatory()
        return super(SaleOrder, self).create(vals_list)
