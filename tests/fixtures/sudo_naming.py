# Fixture for the sudo() naming detector documented in
# agents/odoo-code-review/SKILL.md (Security). Lines carrying the FLAG marker must be
# reported by the grep pipeline; every other line must stay silent.
partner = self.partner_id.sudo()  # FLAG
orders = self.env['sale.order'].sudo().search([('state', '=', 'sale')])  # FLAG
users = records.sudo().mapped('user_id')  # FLAG
    company = self.env.company.sudo()  # FLAG
partner_sudo = self.partner_id.sudo()
orders_sudo = self.env['sale.order'].sudo().search([])
    company_sudo = self.env.company.sudo()
record.sudo().write({'active': False})
self.sudo().write({'state': 'done'})
if partner == other.sudo():
    pass
count = self.env['sale.order'].sudo().search_count([])  # FLAG (scalar - reviewer exempts by hand)
