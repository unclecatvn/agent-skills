from odoo import models


class Base(models.AbstractModel):
    _inherit = 'base'

    def _valid_field_parameter(self, field, name):
        return name == 'tracking' or super()._valid_field_parameter(field, name)
