{
    "name": "POS Hide Product Info",
    "version": "1.0",
    "author": "Preway IT Solutions",
    "category": "Point of Sale",
    "depends": ["point_of_sale"],
    "summary": "This module helps you to hide product info on pos | Hide Product Info on POS | Hide product information on pos screen | Hide Info Button on POS | POS hide product info",
    "description": """
- Hide Product Info on POS
    """,
    "data": [
        "views/pos_config_view.xml",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "pw_pos_hide_product_info/static/src/xml/pos.xml",
        ],
    },
    "price": 5.0,
    "currency": "EUR",
    "application": True,
    "installable": True,
    "license": "LGPL-3",
    "images": ["static/description/Banner.png"],
}
