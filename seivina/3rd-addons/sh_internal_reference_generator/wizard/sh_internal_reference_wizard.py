# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields


class ShInternalReferenceWizard(models.TransientModel):
    _name = 'internal.reference.wizard'
    _description = "Internal Reference Wizard"

    sh_replace_existing = fields.Boolean(string="Replace Existing ?")

    def action_generate_reference(self):
        product_sequence_name = ''
        product_sequence_attribute = ''
        product_sequence_category = ''
        product_sequence_seq = ''
        company_id = self.env.company
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        active_model = context.get('active_model', []) or []
        search_domain_for_product = []
        if active_model == 'product.template':
            search_domain_for_product.append(('id', 'in', active_ids))
        elif active_model == 'product.product':
            search_domain_for_product.append(('id', 'in', active_ids))
        if active_model == 'product.template':
            for template in self.env['product.template'].browse(active_ids):
                product_template_sequence = ''

                if self.sh_replace_existing:
                    if company_id.sh_product_name_config:
                        product_name = str(template.name)
                        if int(company_id.sh_product_name_digit) >= 1:
                            product_name = product_name[:int(
                                company_id.sh_product_name_digit)]
                            if " " in product_name:
                                if company_id.sh_product_name_separate:
                                    product_name = product_name.replace(
                                        " ", str(company_id.sh_product_name_separate))
                                    if company_id.sh_product_sequence_separate:
                                        product_template_sequence = product_template_sequence + \
                                            product_name[:int(
                                                company_id.sh_product_name_digit)] + str(company_id.sh_product_sequence_separate)
                                    else:
                                        product_template_sequence = product_template_sequence + \
                                            product_name[:int(
                                                company_id.sh_product_name_digit)]
                                else:
                                    if company_id.sh_product_sequence_separate:
                                        product_template_sequence = product_template_sequence + \
                                            product_name[:int(
                                                company_id.sh_product_name_digit)] + str(company_id.sh_product_sequence_separate)
                                    else:
                                        product_template_sequence = product_template_sequence + \
                                            product_name[:int(
                                                company_id.sh_product_name_digit)]
                            else:
                                if company_id.sh_product_sequence_separate:
                                    product_template_sequence = product_template_sequence + \
                                        product_name[:int(
                                            company_id.sh_product_name_digit)] + str(company_id.sh_product_sequence_separate)
                                else:
                                    product_template_sequence = product_template_sequence + \
                                        product_name[:int(
                                            company_id.sh_product_name_digit)]
                        product_sequence_name = product_template_sequence
                    product_template_sequence = ''
                    if company_id.sh_product_attribute_config:
                        if int(company_id.sh_product_attribute_name_digit) >= 1:
                            if template.attribute_line_ids:
                                atrributes_name = []
                                for attribute in template.attribute_line_ids:
                                    for value in attribute.value_ids:
                                        atrributes_name.append(value.name)
                                for atrributes_value in atrributes_name:
                                    value = atrributes_value
                                    value = value[:int(
                                        company_id.sh_product_attribute_name_digit)]
                                    if " " in value:
                                        if company_id.sh_product_attribute_name_separate:
                                            value = value.replace(
                                                " ", str(company_id.sh_product_attribute_name_separate))
                                            if company_id.sh_product_sequence_separate:
                                                product_template_sequence += value[:int(company_id.sh_product_attribute_name_digit)] + str(
                                                    company_id.sh_product_sequence_separate)
                                            else:
                                                product_template_sequence += value[:int(
                                                    company_id.sh_product_attribute_name_digit)]
                                        else:
                                            if company_id.sh_product_sequence_separate:
                                                product_template_sequence += value[:int(company_id.sh_product_attribute_name_digit)] + str(
                                                    company_id.sh_product_sequence_separate)
                                            else:
                                                product_template_sequence += value[:int(
                                                    company_id.sh_product_attribute_name_digit)]
                                    else:
                                        if company_id.sh_product_sequence_separate:
                                            product_template_sequence += value[:int(company_id.sh_product_attribute_name_digit)] + str(
                                                company_id.sh_product_sequence_separate)
                                        else:
                                            product_template_sequence += value[:int(
                                                company_id.sh_product_attribute_name_digit)]

                        product_sequence_attribute = product_template_sequence

                    product_template_sequence = ''

                    if company_id.sh_product_cataegory_config:
                        category_name = str(template.categ_id.name)
                        if int(company_id.sh_product_category_digit) >= 1:
                            category_name = category_name[:int(
                                company_id.sh_product_category_digit)]
                            if " " in category_name:
                                if company_id.sh_product_catagory_separate:
                                    category_name = category_name.replace(
                                        " ", str(company_id.sh_product_catagory_separate))
                                    if company_id.sh_product_sequence_separate:
                                        product_template_sequence += category_name[:int(
                                            company_id.sh_product_category_digit)] + str(company_id.sh_product_sequence_separate)
                                    else:
                                        product_template_sequence += category_name[:int(
                                            company_id.sh_product_category_digit)]
                                else:
                                    if company_id.sh_product_sequence_separate:
                                        product_template_sequence += category_name[:int(
                                            company_id.sh_product_category_digit)] + str(company_id.sh_product_sequence_separate)
                                    else:
                                        product_template_sequence += category_name[:int(
                                            company_id.sh_product_category_digit)]
                            else:
                                if company_id.sh_product_sequence_separate:
                                    product_template_sequence += category_name[:int(
                                        company_id.sh_product_category_digit)] + str(company_id.sh_product_sequence_separate)
                                else:
                                    product_template_sequence += category_name[:int(
                                        company_id.sh_product_category_digit)]

                        product_sequence_category = product_template_sequence

                    product_template_sequence = ''

                    if company_id.sh_product_sequence_config and company_id.sh_product_sequence:
                        sequence = self.env['ir.sequence'].next_by_code(
                            company_id.sh_product_sequence.code)
                        product_template_sequence += str(sequence)
                        product_sequence_seq = product_template_sequence

                    seq_list = []
                    seq_name_list = []
                    if product_sequence_name:
                        seq_list.append(self.env.company.sh_product_name_seq)
                        seq_name_list.append(product_sequence_name)
                    if product_sequence_attribute:
                        seq_list.append(
                            self.env.company.sh_product_attribute_name_seq)
                        seq_name_list.append(product_sequence_attribute)
                    if product_sequence_category:
                        seq_list.append(
                            self.env.company.sh_product_catagory_name_seq)
                        seq_name_list.append(product_sequence_category)
                    if product_sequence_seq:
                        seq_list.append(
                            self.env.company.sh_product_sequence_seq)
                        seq_name_list.append(product_sequence_seq)

                    zipped_pairs = zip(seq_list, seq_name_list)

                    result_seq_name_list = [x for _, x in sorted(zipped_pairs)]
                    product_code_str = ''.join(
                        [str(elem) for elem in result_seq_name_list])
                    if product_code_str.endswith(str(self.env.company.sh_product_sequence_separate)):
                        product_code_str = product_code_str[:-1]
                    if product_code_str != '':
                        template.sudo().write({
                            'default_code': product_code_str,
                        })

                else:
                    if not template.default_code:
                        product_name = str(template.name)
                        if int(company_id.sh_product_name_digit) >= 1:
                            product_name = product_name[:int(
                                company_id.sh_product_name_digit)]
                            if " " in product_name:
                                if company_id.sh_product_name_separate:
                                    product_name = product_name.replace(
                                        " ", str(company_id.sh_product_name_separate))
                                    if company_id.sh_product_sequence_separate:
                                        product_template_sequence += product_name[:int(
                                            company_id.sh_product_name_digit)] + str(company_id.sh_product_sequence_separate)
                                    else:
                                        product_template_sequence += product_name[:int(
                                            company_id.sh_product_name_digit)]
                                else:
                                    if company_id.sh_product_sequence_separate:
                                        product_template_sequence += product_name[:int(
                                            company_id.sh_product_name_digit)] + str(company_id.sh_product_sequence_separate)
                                    else:
                                        product_template_sequence += product_name[:int(
                                            company_id.sh_product_name_digit)]
                            else:
                                if company_id.sh_product_sequence_separate:
                                    product_template_sequence += product_name[:int(
                                        company_id.sh_product_name_digit)] + str(company_id.sh_product_sequence_separate)
                                else:
                                    product_template_sequence += product_name[:int(
                                        company_id.sh_product_name_digit)]

                            product_sequence_name = product_template_sequence

                        product_template_sequence = ''

                        if company_id.sh_product_attribute_config:
                            if int(company_id.sh_product_attribute_name_digit) >= 1:
                                if template.attribute_line_ids:
                                    atrributes_name = []
                                    for attribute in template.attribute_line_ids:
                                        for value in attribute.value_ids:
                                            atrributes_name.append(value.name)
                                    for atrributes_value in atrributes_name:
                                        value = atrributes_value
                                        value = value[:int(
                                            company_id.sh_product_attribute_name_digit)]
                                        if " " in value:
                                            if company_id.sh_product_attribute_name_separate:
                                                value = value.replace(
                                                    " ", str(company_id.sh_product_attribute_name_separate))
                                                if company_id.sh_product_sequence_separate:
                                                    product_template_sequence += value[:int(company_id.sh_product_attribute_name_digit)] + str(
                                                        company_id.sh_product_sequence_separate)
                                                else:
                                                    product_template_sequence += product_name[:int(
                                                        company_id.sh_product_attribute_name_digit)]
                                            else:
                                                if company_id.sh_product_sequence_separate:
                                                    product_template_sequence += value[:int(company_id.sh_product_attribute_name_digit)] + str(
                                                        company_id.sh_product_sequence_separate)
                                                else:
                                                    product_template_sequence += product_name[:int(
                                                        company_id.sh_product_attribute_name_digit)]
                                        else:
                                            if company_id.sh_product_sequence_separate:
                                                product_template_sequence += value[:int(company_id.sh_product_attribute_name_digit)] + str(
                                                    company_id.sh_product_sequence_separate)
                                            else:
                                                product_template_sequence += value[:int(
                                                    company_id.sh_product_attribute_name_digit)]

                            product_sequence_attribute = product_template_sequence

                        product_template_sequence = ''

                        if company_id.sh_product_cataegory_config:
                            category_name = str(template.categ_id.name)
                            if int(company_id.sh_product_category_digit) >= 1:
                                category_name = category_name[:int(
                                    company_id.sh_product_category_digit)]
                                if " " in category_name:
                                    if company_id.sh_product_catagory_separate:
                                        category_name = category_name.replace(
                                            " ", str(company_id.sh_product_catagory_separate))
                                        if company_id.sh_product_sequence_separate:
                                            product_template_sequence += category_name[:int(
                                                company_id.sh_product_category_digit)] + str(company_id.sh_product_sequence_separate)
                                        else:
                                            product_template_sequence += category_name[:int(
                                                company_id.sh_product_category_digit)]
                                    else:
                                        if company_id.sh_product_sequence_separate:
                                            product_template_sequence += category_name[:int(
                                                company_id.sh_product_category_digit)] + str(company_id.sh_product_sequence_separate)
                                        else:
                                            product_template_sequence += category_name[:int(
                                                company_id.sh_product_category_digit)]
                                else:
                                    if company_id.sh_product_sequence_separate:
                                        product_template_sequence += category_name[:int(
                                            company_id.sh_product_category_digit)] + str(company_id.sh_product_sequence_separate)
                                    else:
                                        product_template_sequence += category_name[:int(
                                            company_id.sh_product_category_digit)]

                            product_sequence_category = product_template_sequence

                        product_template_sequence = ''

                        if company_id.sh_product_sequence_config and company_id.sh_product_sequence:
                            sequence = self.env['ir.sequence'].next_by_code(
                                company_id.sh_product_sequence.code)
                            product_template_sequence += str(sequence)
                            product_sequence_seq = product_template_sequence

                        seq_list = []
                        seq_name_list = []
                        if product_sequence_name:
                            seq_list.append(
                                self.env.company.sh_product_name_seq)
                            seq_name_list.append(product_sequence_name)
                        if product_sequence_attribute:
                            seq_list.append(
                                self.env.company.sh_product_attribute_name_seq)
                            seq_name_list.append(product_sequence_attribute)
                        if product_sequence_category:
                            seq_list.append(
                                self.env.company.sh_product_catagory_name_seq)
                            seq_name_list.append(product_sequence_category)
                        if product_sequence_seq:
                            seq_list.append(
                                self.env.company.sh_product_sequence_seq)
                            seq_name_list.append(product_sequence_seq)

                        zipped_pairs = zip(seq_list, seq_name_list)

                        result_seq_name_list = [
                            x for _, x in sorted(zipped_pairs)]
                        product_code_str = ''.join(
                            [str(elem) for elem in result_seq_name_list])
                        if product_code_str.endswith(str(self.env.company.sh_product_sequence_separate)):
                            product_code_str = product_code_str[:-1]
                        if product_code_str != '':
                            template.sudo().write({
                                'default_code': product_code_str,
                            })

        elif active_model in ('product.product', 'res.config.settings'):
            # Your logic here
            for product in self.env['product.product'].sudo().search(search_domain_for_product):
                product_sequence = ''
                if self.sh_replace_existing:
                    if company_id.sh_product_name_config:
                        product_name = str(product.name)
                        if int(company_id.sh_product_name_digit) >= 1:
                            product_name = product_name[:int(
                                company_id.sh_product_name_digit)]
                            if " " in product_name:
                                if company_id.sh_product_name_separate:
                                    product_name = product_name.replace(
                                        " ", str(company_id.sh_product_name_separate))
                                    if company_id.sh_product_sequence_separate:
                                        product_sequence = product_sequence + \
                                            product_name[:int(
                                                company_id.sh_product_name_digit)] + str(company_id.sh_product_sequence_separate)
                                    else:
                                        product_sequence = product_sequence + \
                                            product_name[:int(
                                                company_id.sh_product_name_digit)]
                                else:
                                    if company_id.sh_product_sequence_separate:
                                        product_sequence = product_sequence + \
                                            product_name[:int(
                                                company_id.sh_product_name_digit)] + str(company_id.sh_product_sequence_separate)
                                    else:
                                        product_sequence = product_sequence + \
                                            product_name[:int(
                                                company_id.sh_product_name_digit)]
                            else:
                                if company_id.sh_product_sequence_separate:
                                    product_sequence = product_sequence + \
                                        product_name[:int(
                                            company_id.sh_product_name_digit)] + str(company_id.sh_product_sequence_separate)
                                else:
                                    product_sequence = product_sequence + \
                                        product_name[:int(
                                            company_id.sh_product_name_digit)]

                        product_sequence_name = product_sequence

                    product_sequence = ''

                    if company_id.sh_product_attribute_config:
                        if int(company_id.sh_product_attribute_name_digit) >= 1:
                            if product.product_template_attribute_value_ids:
                                atrributes_name = []
                                for attribute in product.product_template_attribute_value_ids:
                                    for value in attribute.product_attribute_value_id:
                                        atrributes_name.append(value.name)
                                for atrributes_value in atrributes_name:
                                    value = atrributes_value
                                    value = value[:int(
                                        company_id.sh_product_attribute_name_digit)]
                                    if " " in value:
                                        if company_id.sh_product_attribute_name_separate:
                                            value = value.replace(
                                                " ", str(company_id.sh_product_attribute_name_separate))
                                            if company_id.sh_product_sequence_separate:
                                                product_sequence += value[:int(company_id.sh_product_attribute_name_digit)] + str(
                                                    company_id.sh_product_sequence_separate)
                                            else:
                                                product_sequence += value[:int(
                                                    company_id.sh_product_attribute_name_digit)]
                                        else:
                                            if company_id.sh_product_sequence_separate:
                                                product_sequence += value[:int(company_id.sh_product_attribute_name_digit)] + str(
                                                    company_id.sh_product_sequence_separate)
                                            else:
                                                product_sequence += value[:int(
                                                    company_id.sh_product_attribute_name_digit)]
                                    else:
                                        if company_id.sh_product_sequence_separate:
                                            product_sequence += value[:int(company_id.sh_product_attribute_name_digit)] + str(
                                                company_id.sh_product_sequence_separate)
                                        else:
                                            product_sequence += value[:int(
                                                company_id.sh_product_attribute_name_digit)]

                        product_sequence_attribute = product_sequence

                    product_sequence = ''

                    if company_id.sh_product_cataegory_config:
                        category_name = str(product.categ_id.name)
                        if int(company_id.sh_product_category_digit) >= 1:
                            category_name = category_name[:int(
                                company_id.sh_product_category_digit)]
                            if " " in category_name:
                                if company_id.sh_product_catagory_separate:
                                    category_name = category_name.replace(
                                        " ", str(company_id.sh_product_catagory_separate))
                                    if company_id.sh_product_sequence_separate:
                                        product_sequence += category_name[:int(company_id.sh_product_category_digit)] + str(
                                            company_id.sh_product_sequence_separate)
                                    else:
                                        product_sequence += category_name[:int(
                                            company_id.sh_product_category_digit)]
                                else:
                                    if company_id.sh_product_sequence_separate:
                                        product_sequence += category_name[:int(company_id.sh_product_category_digit)] + str(
                                            company_id.sh_product_sequence_separate)
                                    else:
                                        product_sequence += category_name[:int(
                                            company_id.sh_product_category_digit)]
                            else:
                                if company_id.sh_product_sequence_separate:
                                    product_sequence += category_name[:int(company_id.sh_product_category_digit)] + str(
                                        company_id.sh_product_sequence_separate)
                                else:
                                    product_sequence += category_name[:int(
                                        company_id.sh_product_category_digit)]

                        product_sequence_category = product_sequence

                    product_sequence = ''

                    if company_id.sh_product_sequence_config and company_id.sh_product_sequence:
                        sequence = self.env['ir.sequence'].next_by_code(
                            company_id.sh_product_sequence.code)
                        product_sequence += str(sequence)
                        product_sequence_seq = product_sequence

                    seq_list = []
                    seq_name_list = []
                    if product_sequence_name:
                        seq_list.append(self.env.company.sh_product_name_seq)
                        seq_name_list.append(product_sequence_name)
                    if product_sequence_attribute:
                        seq_list.append(
                            self.env.company.sh_product_attribute_name_seq)
                        seq_name_list.append(product_sequence_attribute)
                    if product_sequence_category:
                        seq_list.append(
                            self.env.company.sh_product_catagory_name_seq)
                        seq_name_list.append(product_sequence_category)
                    if product_sequence_seq:
                        seq_list.append(
                            self.env.company.sh_product_sequence_seq)
                        seq_name_list.append(product_sequence_seq)

                    zipped_pairs = zip(seq_list, seq_name_list)

                    result_seq_name_list = [x for _, x in sorted(zipped_pairs)]
                    product_code_str = ''.join(
                        [str(elem) for elem in result_seq_name_list])
                    if product_code_str.endswith(str(self.env.company.sh_product_sequence_separate)):
                        product_code_str = product_code_str[:-1]
                    if product_code_str != '':
                        product.sudo().write({
                            'default_code': product_code_str,
                        })

                else:
                    if not product.default_code:
                        product_name = str(product.name)
                        if int(company_id.sh_product_name_digit) >= 1:
                            product_name = product_name[:int(
                                company_id.sh_product_name_digit)]
                            if " " in product_name:
                                if company_id.sh_product_name_separate:
                                    product_name = product_name.replace(
                                        " ", str(company_id.sh_product_name_separate))
                                    if company_id.sh_product_sequence_separate:
                                        product_sequence += product_name[:int(company_id.sh_product_name_digit)] + str(
                                            company_id.sh_product_sequence_separate)
                                    else:
                                        product_sequence += product_name[:int(
                                            company_id.sh_product_name_digit)]
                                else:
                                    if company_id.sh_product_sequence_separate:
                                        product_sequence += product_name[:int(company_id.sh_product_name_digit)] + str(
                                            company_id.sh_product_sequence_separate)
                                    else:
                                        product_sequence += product_name[:int(
                                            company_id.sh_product_name_digit)]
                            else:
                                if company_id.sh_product_sequence_separate:
                                    product_sequence += product_name[:int(company_id.sh_product_name_digit)] + str(
                                        company_id.sh_product_sequence_separate)
                                else:
                                    product_sequence += product_name[:int(
                                        company_id.sh_product_name_digit)]

                            product_sequence_name = product_sequence

                        product_sequence = ''

                        if company_id.sh_product_attribute_config:
                            if int(company_id.sh_product_attribute_name_digit) >= 1:
                                if product.product_template_attribute_value_ids:
                                    atrributes_name = []
                                    for attribute in product.product_template_attribute_value_ids:
                                        for value in attribute.product_attribute_value_id:
                                            atrributes_name.append(value.name)
                                    for atrributes_value in atrributes_name:
                                        value = atrributes_value
                                        value = value[:int(
                                            company_id.sh_product_attribute_name_digit)]
                                        if " " in value:
                                            if company_id.sh_product_attribute_name_separate:
                                                value = value.replace(
                                                    " ", str(company_id.sh_product_attribute_name_separate))
                                                if company_id.sh_product_sequence_separate:
                                                    product_sequence += value[:int(company_id.sh_product_attribute_name_digit)] + str(
                                                        company_id.sh_product_sequence_separate)
                                                else:
                                                    product_sequence += product_name[:int(
                                                        company_id.sh_product_attribute_name_digit)]
                                            else:
                                                if company_id.sh_product_sequence_separate:
                                                    product_sequence += value[:int(company_id.sh_product_attribute_name_digit)] + str(
                                                        company_id.sh_product_sequence_separate)
                                                else:
                                                    product_sequence += product_name[:int(
                                                        company_id.sh_product_attribute_name_digit)]
                                        else:
                                            if company_id.sh_product_sequence_separate:
                                                product_sequence += value[:int(company_id.sh_product_attribute_name_digit)] + str(
                                                    company_id.sh_product_sequence_separate)
                                            else:
                                                product_sequence += value[:int(
                                                    company_id.sh_product_attribute_name_digit)]

                            product_sequence_attribute = product_sequence

                        product_sequence = ''
                        if company_id.sh_product_cataegory_config:
                            category_name = str(product.categ_id.name)
                            if int(company_id.sh_product_category_digit) >= 1:
                                category_name = category_name[:int(
                                    company_id.sh_product_category_digit)]
                                if " " in category_name:
                                    if company_id.sh_product_catagory_separate:
                                        category_name = category_name.replace(
                                            " ", str(company_id.sh_product_catagory_separate))
                                        if company_id.sh_product_sequence_separate:
                                            product_sequence += category_name[:int(company_id.sh_product_category_digit)] + str(
                                                company_id.sh_product_sequence_separate)
                                        else:
                                            product_sequence += category_name[:int(
                                                company_id.sh_product_category_digit)]
                                    else:
                                        if company_id.sh_product_sequence_separate:
                                            product_sequence += category_name[:int(company_id.sh_product_category_digit)] + str(
                                                company_id.sh_product_sequence_separate)
                                        else:
                                            product_sequence += category_name[:int(
                                                company_id.sh_product_category_digit)]
                                else:
                                    if company_id.sh_product_sequence_separate:
                                        product_sequence += category_name[:int(company_id.sh_product_category_digit)] + str(
                                            company_id.sh_product_sequence_separate)
                                    else:
                                        product_sequence += category_name[:int(
                                            company_id.sh_product_category_digit)]

                            product_sequence_category = product_sequence

                        product_sequence = ''

                        if company_id.sh_product_sequence_config and company_id.sh_product_sequence:
                            sequence = self.env['ir.sequence'].next_by_code(
                                company_id.sh_product_sequence.code)
                            product_sequence += str(sequence)
                            product_sequence_seq = product_sequence

                        seq_list = []
                        seq_name_list = []
                        if product_sequence_name:
                            seq_list.append(
                                self.env.company.sh_product_name_seq)
                            seq_name_list.append(product_sequence_name)
                        if product_sequence_attribute:
                            seq_list.append(
                                self.env.company.sh_product_attribute_name_seq)
                            seq_name_list.append(product_sequence_attribute)
                        if product_sequence_category:
                            seq_list.append(
                                self.env.company.sh_product_catagory_name_seq)
                            seq_name_list.append(product_sequence_category)
                        if product_sequence_seq:
                            seq_list.append(
                                self.env.company.sh_product_sequence_seq)
                            seq_name_list.append(product_sequence_seq)

                        zipped_pairs = zip(seq_list, seq_name_list)

                        result_seq_name_list = [
                            x for _, x in sorted(zipped_pairs)]
                        product_code_str = ''.join(
                            [str(elem) for elem in result_seq_name_list])
                        if product_code_str.endswith(str(self.env.company.sh_product_sequence_separate)):
                            product_code_str = product_code_str[:-1]
                        if product_code_str != '':
                            product.sudo().write({
                                'default_code': product_code_str,
                            })
