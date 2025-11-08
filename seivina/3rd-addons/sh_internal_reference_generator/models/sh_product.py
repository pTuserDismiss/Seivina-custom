# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, api


class ShProduct(models.Model):
    _inherit = 'product.product'

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for rec in res:
            if not rec.default_code and self.env.company and self.env.company.sh_product_int_ref_generator and self.env.company.sh_new_product_int_ref_generator:
                product_sequence_name = ''
                product_sequence_attribute = ''
                product_sequence_category = ''
                product_sequence_seq = ''
                product_sequence = ''
                if self.env.company.sh_product_name_config:
                    product_name = str(rec.name)
                    if int(self.env.company.sh_product_name_digit) >= 1:
                        product_name = product_name[:int(
                            self.env.company.sh_product_name_digit)]
                        if " " in product_name:
                            if self.env.company.sh_product_name_separate:
                                product_name = product_name.replace(
                                    " ", str(self.env.company.sh_product_name_separate))
                                if self.env.company.sh_product_sequence_separate:
                                    product_sequence = product_sequence + \
                                        product_name[:int(self.env.company.sh_product_name_digit)] + str(
                                            self.env.company.sh_product_sequence_separate)
                                else:
                                    product_sequence = product_sequence + \
                                        product_name[:int(
                                            self.env.company.sh_product_name_digit)]
                            else:
                                if self.env.company.sh_product_sequence_separate:
                                    product_sequence = product_sequence + \
                                        product_name[:int(self.env.company.sh_product_name_digit)] + str(
                                            self.env.company.sh_product_sequence_separate)
                                else:
                                    product_sequence = product_sequence + \
                                        product_name[:int(
                                            self.env.company.sh_product_name_digit)]
                        else:
                            if self.env.company.sh_product_sequence_separate:
                                product_sequence = product_sequence + \
                                    product_name[:int(self.env.company.sh_product_name_digit)] + str(
                                        self.env.company.sh_product_sequence_separate)
                            else:
                                product_sequence = product_sequence + \
                                    product_name[:int(
                                        self.env.company.sh_product_name_digit)]
                    if product_sequence:
                        product_sequence_name = product_sequence

                product_sequence = ''
                if self.env.company.sh_product_attribute_config:
                    if int(self.env.company.sh_product_attribute_name_digit) >= 1:
                        if rec.product_template_attribute_value_ids:
                            atrributes_name = []
                            for attribute in rec.product_template_attribute_value_ids:
                                for value in attribute.product_attribute_value_id:
                                    atrributes_name.append(value.name)
                            for atrributes_value in atrributes_name:
                                value = atrributes_value
                                value = value[:int(
                                    self.env.company.sh_product_attribute_name_digit)]
                                if " " in value:
                                    if self.env.company.sh_product_attribute_name_separate:
                                        value = value.replace(
                                            " ", str(self.env.company.sh_product_attribute_name_separate))
                                        if self.env.company.sh_product_sequence_separate:
                                            product_sequence += value[:int(self.env.company.sh_product_attribute_name_digit)] + str(
                                                self.env.company.sh_product_sequence_separate)
                                        else:
                                            product_sequence += value[:int(
                                                self.env.company.sh_product_attribute_name_digit)]
                                    else:
                                        if self.env.company.sh_product_sequence_separate:
                                            product_sequence += value[:int(self.env.company.sh_product_attribute_name_digit)] + str(
                                                self.env.company.sh_product_sequence_separate)
                                        else:
                                            product_sequence += value[:int(
                                                self.env.company.sh_product_attribute_name_digit)]
                                else:
                                    if self.env.company.sh_product_sequence_separate:
                                        product_sequence += value[:int(self.env.company.sh_product_attribute_name_digit)] + str(
                                            self.env.company.sh_product_sequence_separate)
                                    else:
                                        product_sequence += value[:int(
                                            self.env.company.sh_product_attribute_name_digit)]
                    if product_sequence:
                        product_sequence_attribute = product_sequence

                product_sequence = ''
                if self.env.company.sh_product_cataegory_config:
                    category_name = str(rec.categ_id.name)
                    if int(self.env.company.sh_product_category_digit) >= 1:
                        category_name = category_name[:int(
                            self.env.company.sh_product_category_digit)]
                        if " " in category_name:
                            if self.env.company.sh_product_catagory_separate:
                                category_name = category_name.replace(
                                    " ", str(self.env.company.sh_product_catagory_separate))
                                if self.env.company.sh_product_sequence_separate:
                                    product_sequence += category_name[:int(self.env.company.sh_product_category_digit)] + str(
                                        self.env.company.sh_product_sequence_separate)
                                else:
                                    product_sequence += category_name[:int(
                                        self.env.company.sh_product_category_digit)]
                            else:
                                if self.env.company.sh_product_sequence_separate:
                                    product_sequence += category_name[:int(self.env.company.sh_product_category_digit)] + str(
                                        self.env.company.sh_product_sequence_separate)
                                else:
                                    product_sequence += category_name[:int(
                                        self.env.company.sh_product_category_digit)]
                        else:
                            if self.env.company.sh_product_sequence_separate:
                                product_sequence += category_name[:int(self.env.company.sh_product_category_digit)] + str(
                                    self.env.company.sh_product_sequence_separate)
                            else:
                                product_sequence += category_name[:int(
                                    self.env.company.sh_product_category_digit)]

                    if product_sequence:
                        product_sequence_category = product_sequence
                product_sequence = ''
                if self.env.company.sh_product_sequence_config and self.env.company.sh_product_sequence:
                    sequence = self.env['ir.sequence'].next_by_code(
                        self.env.company.sh_product_sequence.code)
                    product_sequence += str(sequence)
                    if product_sequence:
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
                    seq_list.append(self.env.company.sh_product_sequence_seq)
                    seq_name_list.append(product_sequence_seq)

                zipped_pairs = zip(seq_list, seq_name_list)

                result_seq_name_list = [x for _, x in sorted(zipped_pairs)]
                product_code_str = ''.join(
                    [str(elem) for elem in result_seq_name_list])
                if product_code_str.endswith(str(self.env.company.sh_product_sequence_separate)):
                    product_code_str = product_code_str[:-1]
                if product_code_str != '':
                    rec.default_code = product_code_str
        return res
