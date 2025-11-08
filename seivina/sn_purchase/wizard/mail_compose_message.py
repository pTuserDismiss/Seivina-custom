from odoo import fields, models, api
import ast

class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    vendor_attachments = fields.Many2many('ir.attachment', string='Vendor Attachments')
    avail_vendor_attachments = fields.Many2many(
        comodel_name='ir.attachment',
        string='Available Vendor Attachments',
        compute='compute_avail_vendor_attachments'
    )

    @api.depends('res_ids')
    def compute_avail_vendor_attachments(self):
        for rec in self:
            if rec.model == 'purchase.order':
                res_ids = ast.literal_eval(rec.res_ids)
                if res_ids:
                    po = self.env['purchase.order'].browse(res_ids[0])
                    rec.avail_vendor_attachments = self.env['ir.attachment'].search([
                        ('res_model', '=', 'res.partner'),
                        ('res_id', '=', po.partner_id.id)
                    ])
            if not rec.avail_vendor_attachments:
                rec.avail_vendor_attachments = None

    def action_send_mail(self):
        if self.model == 'purchase.order':
            self.update({
                'attachment_ids': [(fields.Command.link(id)) for id in self.vendor_attachments.ids]
                })
        return super().action_send_mail()
    
    def _compute_attachment_ids(self):
        super()._compute_attachment_ids()
        if self.model == 'purchase.order':
            res_ids = ast.literal_eval(self.res_ids)
            if res_ids:
                po = self.env['purchase.order'].browse(res_ids[0])

                products = po.order_line.product_id
                product_templates = products.product_tmpl_id
                documents = products.product_document_ids | product_templates.product_document_ids
                attachment_ids = documents.ir_attachment_id | self.env.company.purchase_attachment_ids
                self.update({
                    'attachment_ids': [(fields.Command.link(id)) for id in attachment_ids.ids]
                })
