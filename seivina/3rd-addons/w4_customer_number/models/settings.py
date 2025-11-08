from odoo import models, fields, api, SUPERUSER_ID


class Settings(models.TransientModel):
    _inherit = 'res.config.settings'

    prefix = fields.Char(config_parameter="w4_customer_number.prefix")
    suffix = fields.Char(config_parameter="w4_customer_number.suffix")
    sequence_size = fields.Integer(config_parameter="w4_customer_number.sequence_size")
    starting_number = fields.Integer(config_parameter="w4_customer_number.starting_number")
    generate_number_for_new_customers = fields.Boolean(config_parameter="w4_customer_number.generate_number_for_new_customers")

    def generate_numbers(self):
        self.set_values()
        sequence = self.env.ref('w4_customer_number.seq_res_partner')
        if sequence:
            sequence.prefix = self.prefix or sequence.prefix
            sequence.suffix = self.suffix or sequence.suffix
            sequence.padding = self.sequence_size or sequence.padding
            sequence.number_next_actual = self.starting_number or sequence.number_next_actual

        self.env['res.partner'].cron_update_customer_number_ref()

    def set_values(self):
        res = super().set_values()
        sequence = self.env.ref('w4_customer_number.seq_res_partner')
        if sequence:
            sequence.prefix = self.prefix or sequence.prefix
            sequence.suffix = self.suffix or sequence.suffix
            sequence.padding = self.sequence_size or sequence.padding
            sequence.number_next_actual = self.starting_number or sequence.number_next_actual

        return res 