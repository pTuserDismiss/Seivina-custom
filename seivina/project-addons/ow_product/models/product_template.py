from odoo import _, api, fields, models, Command
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    inspection_label = fields.Selection(
        string='Inspection Label',
        selection=[
            ('white', 'White'),
            ('yellow', 'Yellow'),
            ('blue', 'Blue'),
        ],
        tracking=True,
        store=True,
        compute='_compute_inspection_label',
    )

    product_line = fields.Selection(
        [
            ('medical', 'Medical'),
            ('wellness', 'Wellness'),
        ],
        string='Product Line',
        tracking=True,
    )

    inspection_required = fields.Boolean('Inspection Required', tracking=True)

    @api.depends('inspection_required', 'product_line')
    def _compute_inspection_label(self):
        for rec in self:
            if rec.inspection_required:
                rec.inspection_label = 'yellow'
            elif rec.product_line == 'medical':
                rec.inspection_label = 'blue'
            elif rec.product_line == 'wellness':
                rec.inspection_label = 'white'
            else:
                rec.inspection_label = ''

    @api.onchange('inspection_label')
    def _onchange_inspection_label(self):
        receive_route = self.env.ref('ow_product.route_receive_2_steps')
        if not receive_route:
            return
        
        for rec in self:
            if rec.inspection_label == "yellow" and receive_route.id in rec.route_ids.ids:
                rec.route_ids = [(3, receive_route.id)]
            elif receive_route not in rec.route_ids:
                rec.route_ids = [(4, receive_route.id)]

    @api.constrains('attribute_line_ids')
    def _check_bom_attribute_compatibility(self):
        for rec in self:
            bom_lines = self.env['mrp.bom.line'].search([
                ('component_template_id', '=', rec.id)
            ])
            
            if not bom_lines:
                continue

            for bom_line in bom_lines:
                if not bom_line.bom_id.product_tmpl_id:
                    continue

                bom_attr_lines = bom_line.bom_id.product_tmpl_id.valid_product_template_attribute_line_ids
                bom_attributes = bom_attr_lines.attribute_id
                
                comp_attr_lines = rec.valid_product_template_attribute_line_ids
                component_attributes = comp_attr_lines.attribute_id
                
                common_attributes = bom_attributes & component_attributes
                
                error_messages = []
                
                for attribute in common_attributes:
                    bom_attribute_line = bom_attr_lines.filtered(lambda x: x.attribute_id == attribute)
                    bom_values = bom_attribute_line.product_template_value_ids.product_attribute_value_id
                    
                    comp_attribute_line = comp_attr_lines.filtered(lambda x: x.attribute_id == attribute)
                    comp_values = comp_attribute_line.product_template_value_ids.product_attribute_value_id
                    
                    missing_values = bom_values - comp_values
                    
                    if missing_values:
                        error_messages.append(_(
                            'Attribute "%(attr)s": missing values %(missing_values)s',
                            attr=attribute.name,
                            missing_values=', '.join(missing_values.mapped('name'))
                        ))
                
                if error_messages:
                    raise ValidationError(_(
                        'Product template "%(component)s" should have attribute values that match those of the '
                        'finished goods for the same attributes.',
                        component=rec.name,
                    ))

    #@api.constrains('route_ids')
    #def _check_mismatch_inspection_and_routes(self):
        #receive_route = self.env.ref('ow_product.route_receive_2_steps')
        #if not receive_route:
        #    return

        #for rec in self:
        #    if (rec.inspection_label == 'yellow' and receive_route.id in rec.route_ids.ids) or \
        #        (rec.inspection_label != 'yellow' and receive_route.id not in rec.route_ids.ids):
        #        raise UserError('Mismatch between Inspection Label and Routes. Please check and try again.')

    def copy(self, default=None):
        result = super().copy(default)
        
        for bom in self.bom_ids:
            bom_line_vals = []
            for bom_line in bom.bom_line_ids:
                line_vals = {
                    'product_id': bom_line.product_id.id,
                    'product_qty': bom_line.product_qty,
                    'product_uom_id': bom_line.product_uom_id.id,
                    'sequence': bom_line.sequence,
                    'component_template_id': bom_line.component_template_id.id,
                    'bom_product_template_attribute_value_ids': 
                    [              
                        Command.link(result.attribute_line_ids.product_template_value_ids.filtered(lambda x: x.attribute_id == av.attribute_id \
                            and x.product_attribute_value_id == av.product_attribute_value_id)[:1].id)
                        for av in bom_line.bom_product_template_attribute_value_ids
                    ],
                }
                
                bom_line_vals.append((0, 0, line_vals))
            
            bom_vals = {
                'product_tmpl_id': result.id,
                'bom_line_ids': bom_line_vals,
            }
            
            bom.copy(bom_vals)
            
        return result
