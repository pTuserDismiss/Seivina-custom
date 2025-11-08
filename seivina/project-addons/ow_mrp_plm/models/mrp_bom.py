from lxml import etree

from odoo import _, models, fields, api, _


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.model
    def get_views(self, views, options=None):
        res = super().get_views(views, options)
        
        param = self.env['ir.config_parameter'].sudo().get_param('ow_mrp_plm.prevent_bom_create_edit')
        if param != 'True':
            return res

        if 'form' in res['views']:
            doc = etree.XML(res['views']['form']['arch'])
            for form in doc.xpath("//form"):
                form.set('create', '0')
                form.set('edit', '0')
            res['views']['form']['arch'] = etree.tostring(doc, encoding='unicode')

        if 'list' in res['views']:
            doc = etree.XML(res['views']['list']['arch'])
            for list in doc.xpath("//list"):
                list.set('create', '0')
                list.set('edit', '0')
            res['views']['list']['arch'] = etree.tostring(doc, encoding='unicode')

        return res
