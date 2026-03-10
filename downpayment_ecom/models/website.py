# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class Website(models.Model):
    _inherit = 'website'

    downpayment_enabled = fields.Boolean(string="Enable Downpayment")
    downpayment_type = fields.Selection(
        selection=[
            ('percentage', "Percentage"),
            ('fixed', "Fixed Amount"),
        ],
        string="Downpayment Type",
        default='percentage',
    )
    downpayment_value = fields.Float(string="Downpayment Value", default=30.0)
    downpayment_minimum_amount = fields.Monetary(
        string="Minimum Order Amount",
        currency_field='currency_id',
        help="Only offer downpayment for orders above this amount. Set to 0 to always offer.",
    )
