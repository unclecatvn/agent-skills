from odoo import fields, models


class EventTypeBooth(models.Model):
    _name = 'event.type.booth'
    _description = 'Event Booth Template'

    name = fields.Char(required=True)
    booth_category_id = fields.Many2one('event.booth.category', required=True)
