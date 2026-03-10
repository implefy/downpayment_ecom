# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.sale.controllers import portal as sale_portal


class WebsiteSaleDownpayment(WebsiteSale):

    def _get_shop_payment_values(self, order, **kwargs):
        """Override to pass the downpayment amount to the payment form."""
        values = super()._get_shop_payment_values(order, **kwargs)

        if order.use_downpayment and order.downpayment_available:
            # Re-compute payment values with downpayment as the amount
            is_down_payment = True
            payment_amount = order._get_website_payment_amount()
            payment_values = sale_portal.CustomerPortal._get_payment_values(
                self, order,
                is_down_payment=is_down_payment,
                payment_amount=payment_amount,
                website_id=request.website.id,
            )
            values.update(payment_values)
            values['transaction_route'] = f'/shop/payment/transaction/{order.id}'
            values['landing_route'] = '/shop/payment/validate'
            values['sale_order_id'] = order.id
            values['display_submit_button'] = False

        return values

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
