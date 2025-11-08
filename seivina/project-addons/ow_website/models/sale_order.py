# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    distributor_name = fields.Selection([
            ('primary_distributor', 'Primary Distributor'),
            ('secondary_distributor', 'Secondary Distributor'),
            ('other', 'Other'),
        ],
        string='Name of Distributor or Health System You Are Working With',
    )
    
    other_distributor = fields.Char(
        string='Other Distributor',
        help='Specify distributor name if not in the list',
    )
    
    shipping_service_level = fields.Selection([
            ('dock_to_dock', 'Dock to Dock'),
            ('curbside_liftgate', 'Curbside & Liftgate'),
            ('white_glove', 'White Glove'),
        ],
        string='Shipping Service Level',
    )
    
    business_type = fields.Selection([
            ('dealer_medical', 'Dealer-Medical Equipment'),
            ('hospital', 'Hospital'),
            ('medical_architect', 'Medical Architect/Design'),
            ('surgery_center', 'Surgery Center'),
            ('clinic', 'Clinic'),
            ('physician_practice', 'Physician Practice'),
        ],
        string='Business Type',
    )
    
    tax_exempt = fields.Boolean(
        string='Tax-exempt?',
    )

    show_tax_exempt_banner = fields.Boolean(
        string='Show Tax-exempt Banner',
        default=True,
    )

    quote_message = fields.Text(
        string='Quote Message',
        copy=False,
    )

    def action_confirm_tax_exempt(self):
        for order in self:
            order.message_post(body=_("Tax exemption reviewed and confirmed by %s." % order.user_id.name))
            order.show_tax_exempt_banner = False
    
    def _has_quote_checkout(self):
        return self.website_id.quote_checkout or False

    def _has_customer_user_ids(self):
        return len(self.partner_id.user_ids) > 0

    def get_formview_url(self):
        self.ensure_one()
        return f'/odoo/sales/{str(self.id)}/?view_type=form'

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        
        for order in res:
            if order.website_id and order.website_id.sudo().salesteam_id:
                sales_team = order.website_id.sudo().salesteam_id
                
                if not sales_team.alias_email:
                    continue

                template = self.env.ref('ow_website.email_template_sale_team_assigned_ow_website')
                if not template:
                    continue
                
                template.send_mail(
                    order.id,
                    force_send=True,
                    email_values={
                        'email_to': sales_team.alias_email,
                    },
                    email_layout_xmlid='ow_website.mail_notification_layout_sale_order_ow_website'
                )
        return res
