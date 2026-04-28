# -*- coding: utf-8 -*-
{
    'name': 'chat_bot_integra',
    'version': '1.0.0',
    'summary': """ chat_bot_integra Summary """,
    'author': 'Simon Alberto Rodriguez Pacheco',
    'website': '',
    'category': '',
    'depends': ['base', 'crm', 'web','website','chat_bot_n8n_ia'],
    "data": [
        "security/ir.model.access.csv",
        "views/res_config_settings_view.xml",  # AÑADIDO: El XML debe ir aquí
        "views/login_templates.xml",  # AÑADIDO: El XML debe ir aquí
        "views/remove_powered_by.xml",  # AÑADIDO: El xml para eliminar el footer debe ir aquí
        'views/chatbot_flujo_views.xml',
        'views/chatbot_paso_views.xml',
        'views/partner_view.xml',
        'views/menu_views.xml',
    ],
    'assets': {
        
#         Tu componente:
            # Se monta usando <owl-component> en website.homepage
            # Está registrado en registry.category("public_components")
            # Solo se usa en el frontend del website
        "web.assets_frontend": [
            'chat_bot_integra/static/src/css/chat-bot.css',
            'chat_bot_integra/static/src/js/ChatBotWrapper.js',  
            'chat_bot_integra/static/src/xml/ChatBotWrapper.xml'
            
        ],
        #Si lo usas en el backend (vista CRM, formulario, kanban, etc.), 
        # así que cargarlo en web.assets_backend 
        'web.assets_backend': [
        ],
        
    },
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}