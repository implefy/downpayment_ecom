# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.http import route

from odoo.addons.website_sale.controllers.payment import PaymentPortal


class PaymentPortalDownpayment(PaymentPortal):

    @route()
    def shop_payment_transaction(self, order_id, access_token, **kwargs):
        """Override to set the transaction amount to the downpayment amount.

        When the customer has chosen to pay a downpayment, we inject the
        downpayment amount into kwargs before the parent creates the
        transaction. We also need to bypass the parent's amount validation
        that checks kwargs['amount'] == order.amount_total.
        """
        # We don't call super directly because the parent validates that
        # amount == amount_total. Instead we replicate the flow with our amount.
        from psycopg2.errors import LockNotAvailable

        from odoo import _
        from odoo.exceptions import AccessError, MissingError, UserError, ValidationError
        from odoo.fields import Command
        from odoo.http import request
        from odoo.tools import SQL

        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token)
            request.env.cr.execute(
                SQL('SELECT 1 FROM sale_order WHERE id = %s FOR NO KEY UPDATE NOWAIT', order_id)
            )
        except MissingError:
            raise
        except AccessError as e:
            raise ValidationError(_("The access token is invalid.")) from e
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

        # Determine the payment amount
        if order_sudo.use_downpayment and order_sudo.downpayment_available:
            payment_amount = order_sudo._get_website_payment_amount()
        else:
            payment_amount = order_sudo.amount_total

        if not kwargs.get('amount'):
            kwargs['amount'] = payment_amount

        compare_amounts = order_sudo.currency_id.compare_amounts
        # Validate: amount must match expected payment amount (full or downpayment)
        if compare_amounts(kwargs['amount'], payment_amount):
            raise ValidationError(_("The cart has been updated. Please refresh the page."))
        if compare_amounts(order_sudo.amount_paid, order_sudo.amount_total) == 0:
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
