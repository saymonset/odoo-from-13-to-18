{
    "name": "POS product sequence",
    "version": "1.0",
    "category": "IctecnologyMx",
    "author": "IctecnologyMx",
    "license": "LGPL-3",
    "depends": [
        "point_of_sale",
    ],
    "data": [
        "views/pos_config.xml",
        "views/pos_category_views.xml",
        "views/product_views.xml",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "ic_pos_product_sequence/static/src/**/*",
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
}
