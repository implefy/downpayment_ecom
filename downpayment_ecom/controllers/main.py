# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleDownpayment(WebsiteSale):

    @http.route()
    def shop_payment(self, **post):
        order_sudo = request.cart
        if order_sudo and 'use_downpayment' in post:
            order_sudo.use_downpayment = post.get('use_downpayment') == '1'

        response = super().shop_payment(**post)

        if order_sudo and order_sudo.downpayment_available:
            if hasattr(response, 'qcontext'):
                response.qcontext.update({
                    'downpayment_available': order_sudo.downpayment_available,
                    'downpayment_amount': order_sudo.downpayment_amount,
                    'use_downpayment': order_sudo.use_downpayment,
                    'remaining_amount': order_sudo.amount_total - order_sudo.downpayment_amount,
                })

        return response

    @http.route(
        '/shop/downpayment/toggle',
        type='json',
        auth='public',
        website=True,
    )
    def toggle_downpayment(self, use_downpayment=False):
        order_sudo = request.cart
        if order_sudo and order_sudo.downpayment_available:
            order_sudo.use_downpayment = use_downpayment
            return {
                'success': True,
                'amount_to_pay': order_sudo._get_website_payment_amount(),
                'downpayment_amount': order_sudo.downpayment_amount,
                'remaining_amount': order_sudo.amount_total - order_sudo.downpayment_amount,
            }
        return {'success': False}
