# -*- coding: utf-8 -*-
{
    'name': "pos_my_ticket",

    'summary': "My custom ticket module for Odoo POS",

    'description': """
    My custom ticket module for Odoo POS
    """,

    'author': "Jorge Luis",
    'website': "https://joguenco.dev",

    'category': 'Sales/Point of Sale',
    'version': '0.1',
    'depends': ['point_of_sale'],
    'data': [
        # 'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_my_ticket/static/src/**/*.js',
            'pos_my_ticket/static/src/**/*.xml',
        ],
    },
}

