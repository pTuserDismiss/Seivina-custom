from odoo import fields, models
from ast import literal_eval


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    ticket_type_id = fields.Many2one(
        'helpdesk.ticket.type', string='Ticket Type', check_company=True,
    )
    worksheet_template_id = fields.Many2one(related="ticket_type_id.worksheet_template_id")

    def action_ticket_worksheet(self):
        action = self.worksheet_template_id.action_id.sudo().read()[0]
        worksheet = self.env[self.worksheet_template_id.model_id.sudo().model].search([('x_helpdesk_ticket_id', '=', self.id)])
        context = literal_eval(action.get('context', '{}'))
        action_name = 'Helpdesk Ticket'
        action.update({
            'name': action_name,
            'res_id': worksheet.id if worksheet else False,
            'views': [(False, 'form')],
            'target': 'new',
            'context': {
                **context,
                'edit': True,
                'default_x_helpdesk_ticket_id': self.id,
            },
        })
        return action
