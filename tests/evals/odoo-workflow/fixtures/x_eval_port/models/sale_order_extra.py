from odoo import fields, models


class SaleOrderExtra(models.Model):
    _inherit = ['sale.order']

    x_priority = fields.Boolean()
