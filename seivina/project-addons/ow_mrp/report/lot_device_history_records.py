from odoo import models, api, _
from odoo.exceptions import UserError


class ReportMrpLotDeviceHistoryRecords(models.AbstractModel):
    _name = 'report.ow_mrp.report_lot_device_history_records'
    _description = 'Lot Device History Records Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        done_records = self.env['mrp.production'].search([('state','=','done'),('lot_producing_id','=',docids)])

        if not done_records:
            raise UserError(_("Cannot generate report. No manufacturing record for selected Lot/Serial Number(s)."))

        report_name = 'ow_mrp.report_device_history_records'
        report = self.env['ir.actions.report']._get_report_from_name(report_name)
        return {
            'doc_ids': done_records.ids,
            'doc_model': report.model,
            'docs': done_records,
        }