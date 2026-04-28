# -*- coding: utf-8 -*-
{
    'name': 'chat_bot_n8n_ia',
    'version': '19.0.1.0.0',
    'summary': """ chat_bot_n8n_ia Summary """,
    'author': '',
    'website': '',
    'category': '',
    'depends': ['base', 'web'],
    "data": [
        "security/ir.model.access.csv",
        "views/OpenAIConfig_views.xml"
    ],
    'assets': {
          "web.assets_frontend": [
                  'chat_bot_n8n_ia/static/src/**/*.js',
                  'chat_bot_n8n_ia/static/src/**/*.xml',
                ],
              'web.assets_backend': [
                  'chat_bot_n8n_ia/static/src/**/*.js',
                  'chat_bot_n8n_ia/static/src/**/*.xml',
              ],
              
   
            
          
          },
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
     'images': [
        'chat_bot_n8n_ia/static/description/icon.png'
    ],
}
