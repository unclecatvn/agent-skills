from odoo import api, fields, models


class MailThread(models.AbstractModel):
    _name = 'mail.thread'
    _description = 'Email Thread'

    message_ids = fields.One2many('mail.message', 'res_id', string='Messages')

    def write(self, values):
        self._track_prepare(values)
        return super().write(values)

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, *, body='', subject=None, message_type='notification', **kwargs):
        self._raise_for_invalid_parameters(kwargs)
        return self._message_create([{'body': body}])
