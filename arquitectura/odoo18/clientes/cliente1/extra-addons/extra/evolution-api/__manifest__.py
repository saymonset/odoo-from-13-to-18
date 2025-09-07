# -*- coding: utf-8 -*-
{
    'name': 'WhatsApp Integration with Evolution API',
    'version': '1.0.0',
    'summary': 'Integrate WhatsApp with Evolution API',
    'author': 'Simòn Alberto Rodriguez Pacheco',
    'website': '',
    'category': 'Tools',
    'depends': ['base', 'web', 'react-odoo'], 
    "data": [
        "security/ir.model.access.csv",
        "views/evolution_api_views.xml",
        "views/templates.xml",
        "wizards/WhatsAppComposeMessage.xml"
    ],
    'assets': {
              'web.assets_backend': [
                  'evolution-api/static/src/**/*'
              ],
          },
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
