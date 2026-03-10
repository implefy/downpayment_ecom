# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    downpayment_option = fields.Selection(
        selection=[
            ('default', "Use Default"),
            ('yes', "Allow Downpayment"),
            ('no', "No Downpayment"),
        ],
        string="Downpayment",
        default='default',
        help="Control whether downpayment is allowed for this product on the website.",
    )
    downpayment_percentage_override = fields.Float(
        string="Custom Downpayment %",
        help="Override the global downpayment percentage for this product. Leave at 0 to use the default.",
    )
