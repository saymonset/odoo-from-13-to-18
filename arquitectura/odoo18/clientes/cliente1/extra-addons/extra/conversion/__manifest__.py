# -*- coding: utf-8 -*-
{
    'name': "conversion",
    'summary': "Short (1 phrase/line) summary of the module's purpose",
    'description': """
Long description of module's purpose
    """,
    'author': "Conversion",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Tools',
    'version': '18.0',

    # any module necessary for this one to work correctly
    'depends': ['base','point_of_sale'],

    # always loaded
    "data": [
        "security/conversion_security.xml",
        "security/ir.model.access.csv",
        "views/converssion_views.xml",
       
    ],
     "assets": {
        'point_of_sale.assets': [
            'conversion/static/src/custom_order/custom_order.js',
            'conversion/static/src/**/*',
            
        ],
        "point_of_sale._assets_pos": [
            "conversion/static/src/**/*",
        ],
    },
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

