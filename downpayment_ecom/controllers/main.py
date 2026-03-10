# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleDownpayment(WebsiteSale):

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
