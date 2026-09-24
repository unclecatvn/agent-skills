# Fixture for the odoo-workflow C1 greps. FLAG lines must match; the rest stays silent.
from odoo import http
from odoo.http import route
from odoo.addons.website_sale.controllers import main
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_sale.controllers.main import WebsiteSale as WebsiteSaleBase  # FLAG:controller-class


class XCart(WebsiteSale):  # FLAG:controller-class
    @http.route('/x/cart', type='http', auth='public')  # FLAG:route
    def cart(self, **kw):
        url = '/x/cart'
        return super().cart(**kw)

    @route(['/x/cart/update', '/x/cart'], auth='public')  # FLAG:route
    def cart_update(self, **kw):
        pass

    @route('/x/cart/other')
    def other(self):
        pass


class YCart(main.WebsiteSale):  # FLAG:controller-class
    pass


class ZCart(WebsiteSaleExtra):
    pass


class MixedCart(OtherController, WebsiteSale):  # FLAG:controller-class
    @route(
        route='/x/cart',  # FLAG:route
        auth='public',
    )
    def mixed(self):
        return request.redirect('/x/cart')
