from odoo import fields, models


class ResPartnerExtra(models.Model):
    _inherit = ['res.partner']

    extra_code = fields.Char()
    name = fields.Text()
