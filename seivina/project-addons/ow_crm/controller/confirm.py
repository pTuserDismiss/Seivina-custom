from odoo import http
from odoo.http import request

class LargeOrderConfirmationController(http.Controller):

    @http.route('/odoo/crm/large_order/confirm/<int:lead_id>', type='http', auth='user', website=True)
    def confirm_readiness(self, lead_id, **kwargs):
        Lead = request.env['crm.lead'].sudo()
        lead = Lead.browse(lead_id)
        if not lead.exists():
            return request.not_found()

        person_name = request.env.user.name or 'Someone'

        template = request.env.ref('ow_crm.email_template_large_order_confirmation_to_salesperson')
        if template:
            template.sudo().send_mail(
                lead.id,
                force_send=False,
                email_layout_xmlid='ow_crm.mail_notification_layout_ow',
            )

        return request.render('ow_crm.large_order_thank_you_template', {
            'lead': lead,
            'person_name': person_name,
        })
