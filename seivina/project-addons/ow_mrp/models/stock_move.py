# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    is_substitute = fields.Boolean(string='Substitute', readonly=True, default=False)
    source_ref = fields.Char(string='Source Reference', compute='_compute_source_ref')

    @api.depends('move_orig_ids')
    def _compute_source_ref(self):
        for rec in self:
            orig_move_lines = self.env['stock.traceability.report']._get_move_lines(rec.move_line_ids)
            rec.source_ref = ''
            if orig_move_lines:
                orig_moves = orig_move_lines.move_id.filtered(lambda m: not m.move_orig_ids)
                po_ref_names = orig_moves.filtered(lambda m: m.purchase_line_id).purchase_line_id.order_id.mapped('name')
                mo_ref_names = orig_moves.filtered(lambda m: m.production_id).production_id.mapped('name')
                picking_ref_names = orig_moves.filtered(lambda m: not m.purchase_line_id and not m.production_id).mapped('name')
                rec.source_ref = ','.join(ref for ref in po_ref_names + mo_ref_names + picking_ref_names if ref)
