from odoo import fields, models


class XThingLine(models.Model):
    _name = 'x.thing.line'
    _description = 'Eval thing line'

    thing_id = fields.Many2one('x.thing', required=True, ondelete='cascade')
    thing_note = fields.Text(related='thing_id.x_note')
