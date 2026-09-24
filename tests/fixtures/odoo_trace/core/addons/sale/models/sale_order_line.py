from odoo import fields, models


class SaleOrderLine(models.Model):
    _name = 'sale.order.line'
    _description = "Sales Order Line"

    order_id = fields.Many2one(comodel_name='sale.order', required=True)
    order_partner_id = fields.Many2one(related='order_id.partner_id')
