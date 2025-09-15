# -*- coding: utf-8 -*-
{
    'name': 'React-odoo',
    'version': '1.0.0',
    'summary': """ React-odoo Summary """,
    'author': '',
    'website': '',
    'category': '',
    'depends': ['base', 'web'],
    "data": [
        "security/ir.model.access.csv",
        "views/mi_contacto_views.xml",
        "views/OpenAIConfig_views.xml",
        "views/react_views.xml",
        "views/templates.xml"
    ],
    'assets': {
              'web.assets_backend': [
                  'react-odoo/static/src/css/ItemCunter.css',
                  'react-odoo/static/src/**/*.js',
                  'react-odoo/static/src/**/*.xml',
              ],
            
          
          },
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
