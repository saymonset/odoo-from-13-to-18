# -*- coding: utf-8 -*-
{
    'name': 'T-shirt-postgresql',
    'version': '18.0',
    'summary': """ T-shirt-postgresql Summary """,
    'author': '',
    'website': '',
    'category': '',
    'depends': ['base', 'product','web'],
    "data": [
        "views/templates.xml"
    ],
    'controllers': [
        'controllers/tshirt_controller.py'
    ],
    'assets': {
              'web.assets_backend': [
                  't-shirt-postgresql/static/src/**/*'
              ],
          },
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
