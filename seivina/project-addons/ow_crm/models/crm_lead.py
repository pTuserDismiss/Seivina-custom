from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    is_large_order = fields.Boolean(
        'Is Large Order',
        compute='_compute_is_large_order',
        store=True,
    )

    @api.depends('probability', 'order_ids', 'order_ids.order_line', 'order_ids.order_line.product_uom_qty', 
                'company_id.total_quote_quantity_threshold', 'company_id.probability_threshold')
    def _compute_is_large_order(self):
        for lead in self:
            threshold_qty = lead.company_id.total_quote_quantity_threshold or 0
            threshold_prob = lead.company_id.probability_threshold or 0
            max_qty = lead.get_total_quantity_of_the_biggest_quotation()
            lead.is_large_order = float_compare(max_qty, threshold_qty, precision_digits=2) > 0 and float_compare(lead.probability, threshold_prob, precision_digits=2) > 0
    
    def get_total_quantity_of_the_biggest_quotation(self):
        self.ensure_one()
        total_qty = max((sum(line.product_uom_qty for line in order.order_line) for order in self.order_ids), default=0)
        return total_qty

    def action_send_large_order_notification(self):
        self.ensure_one()
        template = self.env.ref('ow_crm.email_template_large_order', raise_if_not_found=False)
        if not template:
            return
        compose_ctx = dict(
            default_composition_mode='comment',
            default_model='crm.lead',
            default_template_id=template.id,
            default_email_layout_xmlid='ow_crm.mail_notification_layout_ow',
        )
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mail.compose.message',
            'view_mode': 'form',
            'view_id': False,
            'target': 'new',
            'context': compose_ctx,
        }
    
    def get_formview_url(self):
        self.ensure_one()
        return f'/odoo/crm/{str(self.id)}/?view_type=form'

    def confirm_url(self):
        self.ensure_one()
        confirm_url = f'/odoo/crm/large_order/confirm/{self.id}'
        return confirm_url
