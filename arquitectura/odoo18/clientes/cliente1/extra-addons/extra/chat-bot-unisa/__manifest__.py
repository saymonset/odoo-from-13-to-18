# -*- coding: utf-8 -*-
{
    'name': 'chat-bot-unisa',
    'version': '1.0.0',
    'summary': """ chat-bot-unisa Summary """,
    'author': 'Simon Alberto Rodriguez Pacheco',
    'website': '',
    'category': '',
    'depends': ['base', 'web'],
    "data": [
        "security/ir.model.access.csv",
    ],
    'assets': {
          "web.assets_frontend": [
                  'chat-bot-unisa/static/src/css/chat-bot.css',
                  'chat-bot-unisa/static/src/**/*.js',
                  'chat-bot-unisa/static/src/**/*.xml',
                ],
              'web.assets_backend': [
                  'chat-bot-unisa/static/src/css/chat-bot.css',
                  'chat-bot-unisa/static/src/css/ItemCunter.css',
                  'chat-bot-unisa/static/src/**/*.js',
                  'chat-bot-unisa/static/src/**/*.xml',
              ],
              
   
            
          
          },
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
