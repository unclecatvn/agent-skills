from odoo import fields, models

SALE_ORDER_STATE = [
    ('draft', "Quotation"),
    ('sale', "Sales Order"),
    ('cancel', "Cancelled"),
]


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = [
        'portal.mixin',  # comments (with brackets) must not hide the next line
        'mail.thread',
    ]
    _description = "Sales Order"

    state = fields.Selection(selection=SALE_ORDER_STATE, string="Status", default='draft')
    commitment_date = fields.Datetime(string="Delivery Date", copy=False)
    partner_id = fields.Many2one(comodel_name='res.partner', required=True)
    team_id = fields.Many2one(comodel_name='sale.team', string="Sales Team")

    def action_confirm(self):
        self._check_state()
        self.write({'state': 'sale'})
        self._action_confirm()
        return True

    def _action_confirm(self):
        return True

    def message_post(self, **kwargs):
        return super().message_post(**kwargs)
