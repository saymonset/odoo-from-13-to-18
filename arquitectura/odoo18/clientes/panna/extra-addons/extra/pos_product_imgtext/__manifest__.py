{
    "name": "Pos product Image text",
    "version": "1.0",
    "category": "Point of Sale",
    "sequence": 6,
    "author": "ErpMstar Solutions",
    "summary": "Allows you to show product name large text when there is no product image and we can increase or decrease the product box in POS.",
    "description": "Allows you to show product name large text when there is no product image and we can increase or decrease the product box in POS.",
    "depends": ["point_of_sale"],
    "data": [
        # 'security/ir.model.access.csv',
        "views/views.xml",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "pos_product_imgtext/static/src/**/*",
        ],
    },
    "images": [
        "static/description/banner.jpg",
    ],
    "installable": True,
    "website": "",
    "auto_install": False,
    "price": 25,
    "currency": "EUR",
}
