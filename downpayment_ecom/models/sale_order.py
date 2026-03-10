# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.tools import float_round


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    downpayment_available = fields.Boolean(
        string="Downpayment Available",
        compute='_compute_downpayment_available',
    )
    downpayment_amount = fields.Monetary(
        string="Downpayment Amount",
        compute='_compute_downpayment_amount',
        currency_field='currency_id',
    )
    use_downpayment = fields.Boolean(string="Pay Downpayment Only")

    @api.depends('website_id', 'amount_total', 'order_line.product_id')
    def _compute_downpayment_available(self):
        for order in self:
            website = order.website_id
            if not website or not website.downpayment_enabled:
                order.downpayment_available = False
                continue
            if website.downpayment_minimum_amount and order.amount_total < website.downpayment_minimum_amount:
                order.downpayment_available = False
                continue
            # Check if any product explicitly disallows downpayment
            product_lines = order.order_line.filtered(
                lambda l: not l.is_downpayment and l.product_id
            )
            has_blocked = any(
                line.product_id.product_tmpl_id.downpayment_option == 'no'
                for line in product_lines
            )
            order.downpayment_available = not has_blocked

    @api.depends('amount_total', 'website_id', 'order_line.price_total', 'order_line.product_id')
    def _compute_downpayment_amount(self):
        for order in self:
            website = order.website_id
            if not website or not website.downpayment_enabled:
                order.downpayment_amount = 0.0
                continue

            if website.downpayment_type == 'fixed':
                amount = min(website.downpayment_value, order.amount_total)
            else:
                amount = self._compute_percentage_downpayment(order, website)

            precision = order.currency_id.decimal_places if order.currency_id else 2
            order.downpayment_amount = float_round(amount, precision_digits=precision)

    @api.model
    def _compute_percentage_downpayment(self, order, website):
        """Compute downpayment when using percentage mode.

        If any product has a custom override, compute per-line.
        Otherwise use the global percentage on the order total.
        """
        product_lines = order.order_line.filtered(
            lambda l: not l.is_downpayment and l.product_id
        )
        has_overrides = any(
            line.product_id.product_tmpl_id.downpayment_percentage_override > 0
            for line in product_lines
        )
        if not has_overrides:
            return order.amount_total * (website.downpayment_value / 100.0)

        total = 0.0
        for line in product_lines:
            tmpl = line.product_id.product_tmpl_id
            pct = tmpl.downpayment_percentage_override or website.downpayment_value
            total += line.price_total * (pct / 100.0)
        return total

    def _get_website_payment_amount(self):
        """Return the amount the customer should pay on the website."""
        self.ensure_one()
        if self.use_downpayment and self.downpayment_available and self.downpayment_amount:
            return self.downpayment_amount
        return self.amount_total

    def _send_payment_succeeded_for_order_mail(self):
        """Override to generate downpayment invoices after payment."""
        for order in self:
            if order.use_downpayment and order.amount_paid and order.amount_paid < order.amount_total:
                order._generate_downpayment_invoices()
        return super()._send_payment_succeeded_for_order_mail()
