from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = ['sale.order']

    custom_note = fields.Text()

    def _action_confirm(self):
        res = super()._action_confirm()
        self._notify_custom(self.env._('done'))
        return res


class SaleOrderMixed(models.Model):
    _inherit = ['sale.order', 'mail.thread']

    mixed_flag = fields.Boolean()


class SaleCustomTag(models.Model):
    _name = _description = 'sale.custom.tag'

    name = fields.Char()
