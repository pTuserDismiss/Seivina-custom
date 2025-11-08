# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class QualityPoint(models.Model):
    _inherit = 'quality.point'

    show_qt9_reminder = fields.Boolean(string='Show re-upload QT9 reminder')
    
    interval_value = fields.Integer(
        string='Interval Value',
        help="Number of receipts before a quality check is required. For example: 5 means every 5th receipt will be inspected.",
        default=1,
    )
    
    vendor_ids = fields.Many2many(
        'res.partner',
        string='Vendors',
        help="Quality checks will be created based on interval for these specific vendors. If no vendors are selected, the interval applies to all vendors."
    )

    @api.constrains('interval_value', 'vendor_ids', 'measure_frequency_type')
    def _check_interval_values(self):
        for point in self:
            if point.measure_frequency_type == 'interval' and not point.interval_value:
                raise UserError(_('Interval value is required for interval measure frequency type.'))
            if point.measure_frequency_type == 'interval' and not point.vendor_ids:
                raise UserError(_('Vendor is required for interval measure frequency type.'))

    def check_interval_execute_now(self):
        self.ensure_one()
        past = self._count_done_receipts()
        next_number = (past or 0) + 1
        interval = max(self.interval_value or 1, 1)
        return (next_number % interval) == 0

    def check_execute_now(self):
        self.ensure_one()
        
        if self.measure_frequency_type == 'interval':
            return self.check_interval_execute_now()
        
        return super().check_execute_now()

    def _count_done_receipts(self, exclude_picking_id=None):
        vendors = self.vendor_ids
        vendor_contacts = vendors
        for vendor in vendors:
            if vendor.is_company:
                vendor_contacts = vendor_contacts | vendor.child_ids
            elif vendor.parent_id:
                vendor_contacts = vendor_contacts | vendor.parent_id.child_ids
        
        domain = [
            ('product_id', 'in', self.product_ids.ids),
            ('company_id', '=', self.company_id.id),
            ('picking_id.picking_type_id.code', '=', 'incoming'),
            ('picking_id.partner_id', 'in', vendor_contacts.ids),
        ]
        if exclude_picking_id:
            domain.append(('picking_id', '!=', exclude_picking_id))

        groups = self.env['stock.move'].read_group(domain, fields=['picking_id'], groupby=['picking_id'])
        return len(groups)
