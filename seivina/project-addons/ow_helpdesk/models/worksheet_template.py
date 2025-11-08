from odoo import api, models, _


class WorksheetTemplate(models.Model):
    _inherit = 'worksheet.template'

    @api.model
    def _get_helpdesk_ticket_user_group(self):
        return self.env.ref('helpdesk.group_helpdesk_user')

    @api.model
    def _get_helpdesk_ticket_manager_group(self):
        return self.env.ref('helpdesk.group_helpdesk_manager')

    @api.model
    def _get_helpdesk_ticket_access_all_groups(self):
        return self.env.ref('helpdesk.group_helpdesk_manager') | self.env.ref('helpdesk.group_helpdesk_user')

    @api.model
    def _get_helpdesk_ticket_module_name(self):
        return 'ow_helpdesk'

    @api.model
    def _default_helpdesk_ticket_worksheet_form_arch(self):
        return """
            <form create="false">
                <sheet>
                    <h1 invisible="context.get('studio') or context.get('default_x_helpdesk_ticket_id')">
                        <field name="x_helpdesk_ticket_id"/>
                    </h1>
                </sheet>
            </form>
        """
    
    def get_x_model_form_action(self):
        action = super().get_x_model_form_action()
        if self.res_model == 'helpdesk.ticket':
            action['context'].update({
                'action_xml_id': 'ow_helpdesk.helpdesk_worksheet_template_action_settings',
                'worksheet_template_id': self.id,
            })
        return action
