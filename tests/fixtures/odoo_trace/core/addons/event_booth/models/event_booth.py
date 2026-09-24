from odoo import fields, models


class EventBooth(models.Model):
    _name = 'event.booth'
    _inherit = ['event.type.booth', 'mail.thread']
    _description = 'Event Booth'

    partner_id = fields.Many2one('res.partner', string='Renter')
