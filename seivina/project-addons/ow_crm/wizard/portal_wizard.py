from odoo import models, _
from odoo.exceptions import UserError


class PortalWizardUser(models.TransientModel):
    _inherit = 'portal.wizard.user'

    def action_grant_access(self):
        result = self._check_user_access('grant')
        return result or super().action_grant_access()
    
    def action_revoke_access(self):
        result = self._check_user_access('revoke')
        return result or super().action_revoke_access()
    
    def _check_user_access(self, action_type):
        has_sales_admin_access = self.env.user.has_group('sales_team.group_sale_manager')
        if not has_sales_admin_access:
            return self._open_approval_wizard(action_type)
        return False
    
    def _open_approval_wizard(self, action_type):
        self.ensure_one()
        new_wizard = self.env['approval.wizard'].create({
            'res_model': 'res.partner',
            'res_id': self.partner_id.id,
            'allowed_groups': 'sales_team.group_sale_manager',
            'reason': _('Sign-off for %s access', 'granting' if action_type == 'grant' else 'revoking'),
            'method_approved': 'action_{}_access'.format(action_type),
        })
        return new_wizard._get_records_action(name=_('Sign-off Required'), target='new')
