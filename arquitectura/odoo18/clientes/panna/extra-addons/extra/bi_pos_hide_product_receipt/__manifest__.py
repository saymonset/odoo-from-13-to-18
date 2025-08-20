# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
{
    "name": "Hide Product in POS Receipt | Hide Free Product in POS Receipt",
    "version": "18.0.0.0",
    "category": "Point of Sale",
    "summary": "Hide product in point of sales receipt hide products in pos receipt POS Hide Product In Receipt point of sales Hide Product In Receipt pos product hide in receipt free product hide in pos receipt free product hide in receipt pos free product hide receipt",
    "description": """

        POS Hide Product in Receipt in odoo,
        Hide In Receipt in odoo,
        Enable Hide In Receipt in odoo,
        Disable Hide In Receipt in odoo,
        Product Hide from Receipt in odoo,

    """,
    "author": "BROWSEINFO",
    "price": 25,
    "currency": "EUR",
    "website": "https://www.browseinfo.com/demo-request?app=bi_pos_hide_product_receipt&version=18&edition=Community",
    "depends": ["base", "point_of_sale"],
    "data": [
        "views/pos_config.xml",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "bi_pos_hide_product_receipt/static/src/app/pos_orderline.js",
            "bi_pos_hide_product_receipt/static/src/app/orderline.xml",
        ],
    },
    "license": "OPL-1",
    "installable": True,
    "auto_install": False,
    "live_test_url": "https://www.browseinfo.com/demo-request?app=bi_pos_hide_product_receipt&version=18&edition=Community",
    "images": ["static/description/Banner.gif"],
}
