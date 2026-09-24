from odoo import fields, models


class SaleReport(models.Model):
    _name = "sale.report"
    _description = "Sales Analysis Report"
    _auto = False

    date = fields.Datetime(readonly=True)
    order_id = fields.Many2one('sale.order', readonly=True)
