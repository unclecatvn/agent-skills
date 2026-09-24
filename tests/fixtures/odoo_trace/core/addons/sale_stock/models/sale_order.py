from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    partner_id = fields.Many2one(check_company=True)
    state = fields.Selection(selection_add=[('shipped', "Shipped")])

    def _action_confirm(self):
        self._action_launch_stock_rule()
        return super()._action_confirm()
