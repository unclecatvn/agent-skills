from odoo import api, fields, models


class XThing(models.Model):
    _name = 'x.thing'
    _description = 'Eval thing'

    name = fields.Char(required=True)
    x_note = fields.Text()
    x_note_length = fields.Integer(compute='_compute_x_note_length', store=True)

    @api.depends('x_note')
    def _compute_x_note_length(self):
        for thing in self:
            thing.x_note_length = len(thing.x_note or '')
