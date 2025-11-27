{
    "name": "RAG Unisa Theme",
    "version": "18.0.1.0.0",
    "depends": ["web","website","chat-bot-n8n-ia"],
    "category": "Customizations",
    "author": "Yoni Tjio",
    "description": "RAG UNISA Description theme.",
    "data": [
        "views/chat_bot_client_templates.xml",
    ],
    
    "assets": {
        "web.assets_frontend": [
             'chat-bot-n8n-ia/static/src/**/*.js',
             'chat-bot-n8n-ia/static/src/**/*.xml',
        ]
    },
    "installable": True,
    "license": "Other proprietary",
}