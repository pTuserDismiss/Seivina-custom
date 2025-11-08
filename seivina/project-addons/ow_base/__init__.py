from . import models
from odoo import _
from odoo.exceptions import UserError

def _check_core_configs(env):
    IrDefault = env['ir.default'].sudo()
    IrDefault.set(
        'product.template', 'invoice_policy', 'delivery'
    )  # This will also set the Invoicing Policy setting to 'Delivered quantities'

    # Set 2-step outgoing shipment
    internal_user_group = env.ref('base.group_user')
    multi_location_group = env.ref('stock.group_stock_multi_locations')
    multi_route_group = env.ref('stock.group_adv_location')
    internal_user_group._apply_group(multi_location_group)
    internal_user_group._apply_group(multi_route_group)
    warehouses = env['stock.warehouse'].search([('company_id', '=', env.company.id)])
    for warehouse in warehouses:
        warehouse.write({'delivery_steps': 'pick_ship'})
