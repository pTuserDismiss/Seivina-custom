from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    carrier_id = fields.Many2one(
        compute='_compute_carrier_id',
        store=True,
    )

    @api.depends('move_ids_without_package.product_id', 'sale_id.carrier_id')
    def _compute_carrier_id(self):
        for picking in self:
            if picking.state in ('done', 'cancel') or picking.picking_type_code != 'outgoing':
                picking.carrier_id = picking.carrier_id
            else:
                if picking.sale_id.carrier_id:
                    picking.carrier_id = picking.sale_id.carrier_id
                else:
                    carriers = picking.move_ids.product_id._get_default_carrier()
                    picking.carrier_id = carriers and carriers.sorted('sequence')[0] or False

    def action_send_tracking_to_customer(self):
        subtype_id = self.env['ir.model.data']._xmlid_to_res_id('mail.mt_comment')
        template = self.env.ref('stock.mail_template_data_delivery_confirmation')

        for stock_pick in self:
            delivery_template = stock_pick.company_id.stock_mail_confirmation_template_id or template

            if not delivery_template:
                self.message_post(
                    body='Your email template is not available.',
                    subject='',
                    message_type='comment',
                )
                continue

            stock_pick.with_context(force_send=True).message_post_with_source(
                delivery_template,
                email_layout_xmlid='mail.mail_notification_light',
                subtype_id=subtype_id,
            )
