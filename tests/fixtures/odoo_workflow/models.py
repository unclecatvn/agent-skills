# Fixture for the Step 1 grep commands in skills/odoo-workflow/SKILL.md.
# A line tagged FLAG:<command> must be reported by that command; every other line stays silent.
from odoo import fields, models


class XThing(models.Model):
    _name = 'x.thing'  # FLAG:model
    note = fields.Text()  # FLAG:field
    note_ids = fields.One2many('x.thing.line', 'thing_id')


class XThingDescribed(models.AbstractModel):
    _name = _description = 'x.thing'  # FLAG:model


class XThingLine(models.Model):
    _name = 'x.thing.line'
    _inherit = ['mail.thread']
    note = compute_note()


class XThingOneLine(models.Model):
    _inherit = 'x.thing'  # FLAG:inherit
    note: Html = fields.Html()  # FLAG:field


class XThingListOneLine(models.Model):
    _inherit = ['mail.thread', 'x.thing']  # FLAG:inherit


class XThingMultiLine(models.Model):
    _inherit = ['portal.mixin',
                'x.thing',  # FLAG:inherit-multi
                ]


class XThingMultiLineOpen(models.Model):
    _inherit = [
        'mail.activity.mixin',
        'x.thing',  # FLAG:inherit-multi
    ]


class XThingLineExtension(models.Model):
    _inherit = 'x.thing.line'
