# -*- coding: utf-8 -*-
{
    'name': 'T-shirt-postgresql',
    'version': '1.0.0',
    'summary': """ T-shirt-postgresql Summary """,
    'author': '',
    'website': '',
    'category': '',
    'depends': ['base', 'web'],
    "data": [
        "views/templates.xml"
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
