{
    "name": "Downpayment E-commerce",
    "version": "19.0.1.0.0",
    "category": "Website/Website",
    "summary": "Downpayment functionality for e-commerce",
    "depends": [
        "website_sale",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/res_config_settings_views.xml",
        "views/product_template_views.xml",
        "views/templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "downpayment_ecom/static/src/js/downpayment.js",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "LGPL-3",
}
