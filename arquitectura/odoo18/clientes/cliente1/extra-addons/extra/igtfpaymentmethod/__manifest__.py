# -*- coding: utf-8 -*-
{
    'name': 'igtfpaymentmethod',
    'version': '1.0.0',
    'summary': """ Addons_igtfpaymentmethod Summary """,
    'author': 'saymon_set@hotmail.com',
    'website': 'https://www.jumpjibe.com',
    'category': 'igtf',
      'depends': ['base', 'point_of_sale','sale'],

    "data": [
        "security/ir.model.access.csv",
        "views/odoo_services.xml",
        "views/pos_payment_method_views.xml",
        "views/sale_order_view_views.xml",
    ],
    'assets': {
             
                "point_of_sale._assets_pos": [
                     'igtfpaymentmethod/static/src/app/screens/**/*.js',
                     'igtfpaymentmethod/static/src/app/screens/**/*.xml',
                     'igtfpaymentmethod/static/src/config.js',
                     'igtfpaymentmethod/static/src/currencyConverter.js',
                ],
                'web.assets_backend': [
                    'igtfpaymentmethod/static/src/app/dashboard/**/*.js',
                    'igtfpaymentmethod/static/src/app/services/**/*.js',
                    'igtfpaymentmethod/static/src/app/services/**/*.xml',
                    'igtfpaymentmethod/static/src/app/dashboard/**/*.xml',
                ],
            
          },
      
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
