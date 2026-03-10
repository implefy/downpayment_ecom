# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    downpayment_enabled = fields.Boolean(
        related='website_id.downpayment_enabled', readonly=False,
    )
    downpayment_type = fields.Selection(
        related='website_id.downpayment_type', readonly=False,
    )
    downpayment_value = fields.Float(
        related='website_id.downpayment_value', readonly=False,
    )
    downpayment_minimum_amount = fields.Monetary(
        related='website_id.downpayment_minimum_amount', readonly=False,
        currency_field='currency_id',
    )
    currency_id = fields.Many2one(
        related='website_id.currency_id',
    )
