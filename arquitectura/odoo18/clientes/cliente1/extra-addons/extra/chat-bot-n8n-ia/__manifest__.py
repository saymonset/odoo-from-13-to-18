# -*- coding: utf-8 -*-
{
    'name': 'chat-bot-n8n-ia',
    'version': '1.0.0',
    'summary': """ chat-bot-n8n-ia Summary """,
    'author': '',
    'website': '',
    'category': '',
    'depends': ['base', 'web'],
    "data": [
        "security/ir.model.access.csv",
        "views/mi_contacto_views.xml",
        "views/OpenAIConfig_views.xml",
        "views/n8n_chat_bot_views.xml",
        "views/templates.xml"
    ],
    'assets': {
          "web.assets_frontend": [
                  'chat-bot-n8n-ia/static/src/css/chat-bot.css',
                  'chat-bot-n8n-ia/static/src/js/chat_bot_wrapper.js',
                  'chat-bot-n8n-ia/static/src/**/*.js',
                  'chat-bot-n8n-ia/static/src/**/*.xml',
                ],
              'web.assets_backend': [
                  'chat-bot-n8n-ia/static/src/css/chat-bot.css',
                  'chat-bot-n8n-ia/static/src/js/chat_bot_wrapper.js',
                  'chat-bot-n8n-ia/static/src/css/ItemCunter.css',
                  'chat-bot-n8n-ia/static/src/**/*.js',
                  'chat-bot-n8n-ia/static/src/**/*.xml',
              ],
              
   
            
          
          },
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
