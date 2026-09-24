from odoo import fields, models


class PortalMixin(models.AbstractModel):
    _name = 'portal.mixin'
    _description = 'Portal Mixin'

    access_url = fields.Char('Portal Access URL', compute='_compute_access_url')
