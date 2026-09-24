from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    never_loaded = fields.Char()
