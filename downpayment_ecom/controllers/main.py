# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleDownpayment(WebsiteSale):

    @http.route()
    def shop_payment(self, **post):
        order = request.website.sale_get_order()
        if order and 'use_downpayment' in post:
            order.use_downpayment = post.get('use_downpayment') == '1'

        response = super().shop_payment(**post)

        if order and order.downpayment_available:
            if hasattr(response, 'qcontext'):
                response.qcontext.update({
                    'downpayment_available': order.downpayment_available,
                    'downpayment_amount': order.downpayment_amount,
                    'use_downpayment': order.use_downpayment,
                    'remaining_amount': order.amount_total - order.downpayment_amount,
                })

        return response

    @http.route(
        '/shop/downpayment/toggle',
        type='json',
        auth='public',
        website=True,
    )
    def toggle_downpayment(self, use_downpayment=False):
        order = request.website.sale_get_order()
        if order and order.downpayment_available:
            order.use_downpayment = use_downpayment
            return {
                'success': True,
                'amount_to_pay': order._get_website_payment_amount(),
                'downpayment_amount': order.downpayment_amount,
                'remaining_amount': order.amount_total - order.downpayment_amount,
            }
        return {'success': False}
