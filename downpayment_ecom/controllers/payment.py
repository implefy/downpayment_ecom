# Part of Odoo. See LICENSE file for full copyright and licensing details.

from psycopg2.errors import LockNotAvailable

from odoo import _
from odoo.exceptions import AccessError, MissingError, UserError, ValidationError
from odoo.fields import Command
from odoo.http import request, route
from odoo.tools import SQL

from odoo.addons.website_sale.controllers.payment import PaymentPortal


class PaymentPortalDownpayment(PaymentPortal):

    @route()
    def shop_payment_transaction(self, order_id, access_token, **kwargs):
        """Override to charge the downpayment amount instead of the full total.

        When downpayment is not active, delegates entirely to super().
        Only overrides the amount logic — all other steps (locking, validation,
        transaction creation) use the same native helper methods.
        """
        order_sudo = self._document_check_access('sale.order', order_id, access_token)

        if not (order_sudo.use_downpayment and order_sudo.downpayment_available):
            return super().shop_payment_transaction(order_id, access_token, **kwargs)

        # --- Downpayment flow: same as native but with custom amount ---
        try:
            request.env.cr.execute(
                SQL('SELECT 1 FROM sale_order WHERE id = %s FOR NO KEY UPDATE NOWAIT', order_id)
            )
        except LockNotAvailable:
            raise UserError(_("Payment is already being processed."))

        if order_sudo.state == "cancel":
            raise ValidationError(_("The order has been cancelled."))

        order_sudo._check_cart_is_ready_to_be_paid()

        self._validate_transaction_kwargs(kwargs)
        kwargs.update({
            'partner_id': order_sudo.partner_invoice_id.id,
            'currency_id': order_sudo.currency_id.id,
            'sale_order_id': order_id,
        })

        # Use downpayment amount instead of amount_total
        expected_amount = order_sudo._get_website_payment_amount()
        if not kwargs.get('amount'):
            kwargs['amount'] = expected_amount

        compare = order_sudo.currency_id.compare_amounts
        if compare(kwargs['amount'], expected_amount):
            raise ValidationError(_("The cart has been updated. Please refresh the page."))
        if compare(order_sudo.amount_paid, order_sudo.amount_total) == 0:
            raise UserError(_("The cart has already been paid. Please refresh the page."))

        if delay_token_charge := kwargs.get('flow') == 'token':
            request.update_context(delay_token_charge=True)

        tx_sudo = self._create_transaction(
            custom_create_values={'sale_order_ids': [Command.set([order_id])]}, **kwargs,
        )
        request.session['__website_sale_last_tx_id'] = tx_sudo.id
        self._validate_transaction_for_order(tx_sudo, order_sudo)

        if delay_token_charge:
            tx_sudo._charge_with_token()

        return tx_sudo._get_processing_values()
