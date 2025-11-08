from odoo import models, api, _
from odoo.exceptions import UserError


class ReportMrpDeviceHistoryRecords(models.AbstractModel):
    _name = 'report.ow_mrp.report_device_history_records'
    _description = 'Device History Records Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        all_records = self.env['mrp.production'].browse(docids)
        done_records = all_records.filtered(lambda r: r.state == 'done')

        if not done_records:
            raise UserError(_("Cannot generate report. MO(s) not completed."))

        report_name = 'ow_mrp.report_device_history_records'
        report = self.env['ir.actions.report']._get_report_from_name(report_name)
        return {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': done_records,
        }
    