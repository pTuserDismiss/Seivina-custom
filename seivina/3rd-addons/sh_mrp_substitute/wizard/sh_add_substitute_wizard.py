
from odoo import api,fields,models
# import json

class ShAddSubstituteWizard(models.TransientModel):
    _name = 'sh.add.substitute.wizard'
    _description = 'SH Add Substitute Wizard'
    
    sh_raw_product_ids = fields.Many2many('product.product',string='Raw Products')
    sh_product_id = fields.Many2one('product.product',string='Product',required=True, )
    sh_sub_product_ids = fields.Many2many('product.product', 'product_sub_product_rel', string='Raw Products')
    sh_substitute_product_id = fields.Many2one('product.product','Substitute',required=True)
    sh_substitute_product_qty = fields.Float(string='Qty',required=True)
    sh_operation = fields.Selection(
        string='Operation',
        selection=[('replace', 'Replace'), ('add', 'Add')],
        default='add',
    )
    sh_production_id = fields.Many2one('mrp.production')
    
    @api.model
    def default_get(self, fields):
        res = super(ShAddSubstituteWizard, self).default_get(fields)
        if self._context['production_id']:
            res['sh_production_id'] = self.env['mrp.production'].sudo().browse(self._context['production_id']).id
            raw_products = self.env['mrp.production'].sudo().browse(self._context['production_id']).mapped('move_raw_ids').mapped('product_id').ids
            res['sh_raw_product_ids']=[(6,0,raw_products)]
        return res
    
    
    @api.onchange('sh_product_id')
    def _onchange_sh_product_id(self):
        bom_line = self.env['mrp.bom.line'].search([('bom_id','=',self.sh_production_id.bom_id.id),('product_id','=',self.sh_product_id.id)])
        self.sh_sub_product_ids = [(6,0,bom_line.sh_substitute_product_ids.ids)]
        
    @api.onchange('sh_substitute_product_id')
    def _onchange_substitute_product_id(self):
        bom_line = self.env['mrp.bom.line'].search([('bom_id','=',self.sh_production_id.bom_id.id),('product_id','=',self.sh_product_id.id),])
        self.sh_substitute_product_qty = bom_line.sh_substitute_product_qty
    

    def add_substitute(self):
        if self.sh_operation == 'replace':
            move_id = self.env['stock.move'].search([('product_id','=',self.sh_product_id.id),('raw_material_production_id','=',self.sh_production_id.id)])
            move_id.write({'state':'draft'})
            move_id.unlink()
            self.env['stock.move'].create({'product_id':self.sh_substitute_product_id.id,'name':self.sh_substitute_product_id.name ,'product_uom':self.sh_substitute_product_id.uom_id.id ,'product_uom_qty':self.sh_substitute_product_qty,'raw_material_production_id':self.sh_production_id.id,'state':'confirmed'})
        elif self.sh_operation == 'add':
            move_id = self.env['stock.move'].search([('product_id','=',self.sh_product_id.id)],limit=1)
            self.env['stock.move'].create({'product_id':self.sh_substitute_product_id.id,'name':self.sh_substitute_product_id.name ,'product_uom':self.sh_substitute_product_id.uom_id.id ,'product_uom_qty':self.sh_substitute_product_qty,'raw_material_production_id':self.sh_production_id.id,'state':'confirmed'})
        
            # print('No any operation performed.')
