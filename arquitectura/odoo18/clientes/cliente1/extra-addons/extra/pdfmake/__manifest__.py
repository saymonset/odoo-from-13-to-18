# -*- coding: utf-8 -*-
{
    'name': 'Pdfmake',
    'version': '1.0.0',
    'summary': """ Pdfmake Reports """,
    'author': '',
    'website': '',
    'category': 'Tools',
    'depends': ['base'],
     'external_dependencies': {
        'python': ['pdfmake'],
    },
    'data': [
        'views/pdfmake_printer_views.xml',
        'security/ir.model.access.csv',
    ],
    'assets': {
              'web.assets_backend': [
                  'pdfmake/static/src/**/*'
                  'pdfmake/static/src/fonts/*'
              ],
          },
    'post_init_hook': 'post_init_hook',
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
