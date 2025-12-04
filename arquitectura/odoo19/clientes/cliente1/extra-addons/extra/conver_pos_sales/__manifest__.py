# -*- coding: utf-8 -*-
{
    'name': 'Conver_pos_sales',
    'version': '1.0.0',
    'summary': """ Conver_pos_sales Summary """,
    'author': '',
    'website': '',
    'category': '',
    'depends': ['base', 'web'],
    'data': [
        'views/test_test_views.xml',
        'security/ir.model.access.csv'
    ],
    'assets': {
              'web.assets_backend': [
                  'conver_pos_sales/static/src/**/*'
              ],
          },
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
