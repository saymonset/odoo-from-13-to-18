# -*- coding: utf-8 -*-
{
    'name': 'chat_bot_integra',
    'version': '1.0.0',
    'summary': """ chat_bot_integra Summary """,
    'author': 'Simon Alberto Rodriguez Pacheco',
    'website': '',
    'category': '',
    'depends': ['base', 'crm', 'web','website'],
    "data": [
        "security/ir.model.access.csv",
        "views/ChatBotWrapper.xml",  # AÑADIDO: El XML debe ir aquí
        "views/login_templates.xml",  # AÑADIDO: El XML debe ir aquí
    ],
    'assets': {
        "web.assets_frontend": [
            'chat_bot_integra/static/src/css/chat-bot.css',
            'chat_bot_integra/static/src/js/ChatBotWrapper.js',  # Cambiado a ruta específica
            'chat_bot_integra/static/src/js/ChatBotWrapper.js',
        ],
        'web.assets_backend': [
            'chat_bot_integra/static/src/css/chat-bot.css',
            'chat_bot_integra/static/src/js/ChatBotWrapper.js',  # Cambiado a ruta específica
        ],
    },
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}