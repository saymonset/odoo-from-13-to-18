{
    "name": "RAG Unisa Theme",
    "version": "18.0.1.0.0",
    "depends": ["web","website","chat-bot-unisa"],
    "category": "Customizations",
    "author": "Simon Alberto Rodriguez Pacheco",
    "description": "RAG UNISA Description theme.",
    "data": [
        "views/chat_bot_client_templates.xml",
    ],
    
    "assets": {
        "web.assets_frontend": [
             'chat-bot-unisa/static/src/**/*.js',
             'chat-bot-unisa/static/src/**/*.xml',
        ]
    },
    "installable": True,
    "license": "Other proprietary",
}