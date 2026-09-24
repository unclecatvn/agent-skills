from odoo import fields, models


class Partner(models.Model):
    _name = 'res.partner'
    _description = 'Contact'

    name = fields.Char()
    country_id: Country = fields.Many2one('res.country', string='Country')


class Users(models.Model):
    _name = 'res.users'
    _inherits = {'res.partner': 'partner_id'}

    partner_id = fields.Many2one('res.partner', required=True)
