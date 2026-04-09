# -*- coding: utf-8 -*-
{
    'name': 'Frontend',
    'description': 'frontend Custom theme for Hotel Jump N Jibe in Playa El Yaque',
    'category': 'Website/Theme',
    'version': '19.0.1.0.0',
    'author': 'Integraia',
    'summary': 'frontend Theme for Hotel Jump N Jibe',
    'depends': ['base', 'web','website'],
    'data': [
        'security/ir.model.access.csv',
        'views/snippets.xml',
        'views/pages.xml',
    ],
    'assets': {
              'web.assets_backend': [
                  'frontend/static/src/**/*'
              ],
            'web.assets_frontend': [
            'frontend/static/src/css/style.css',
        ],
          },
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
