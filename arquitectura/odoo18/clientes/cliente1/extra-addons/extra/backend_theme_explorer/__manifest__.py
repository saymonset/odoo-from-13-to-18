{
    "name": "Explorer Backend Theme",
    "version": "18.0.1.0.0",
    "depends": ["web","website", "auth_signup", "chat-bot-n8n-ia"],
    "category": "Customizations",
    "author": "Yoni Tjio",
    "description": "Explorer backend theme.",
    "data": [
        "views/menu.xml",
        "views/res_config_settings_views.xml",
        "views/login_templates.xml",
    ],
    "assets": {
            "backend_theme_explorer.assets_login": [
            "backend_theme_explorer/static/src/css/o_call_chat_bot.css",
            "backend_theme_explorer/static/src/components/call_chat_bot_app/CallChatBotApp.js",
            "backend_theme_explorer/static/src/components/public/public_chatbot.js",
            'backend_theme_explorer/static/src/components/call_chat_bot_app/CallChatBotApp.js',
            'backend_theme_explorer/static/src/components/call_chat_bot_app/CallChatBotApp.xml',
        ],
        "web.assets_frontend": [
            ("include", "web._assets_bootstrap_frontend"),
            "backend_theme_explorer/static/fonts/poppins.css",
            "backend_theme_explorer/static/src/scss/login.scss",
            'backend_theme_explorer/static/src/components/call_chat_bot_app/CallChatBotApp.js',
            'backend_theme_explorer/static/src/components/call_chat_bot_app/CallChatBotApp.xml',
        ],
        "web.assets_login": [
            # ChatBot visible en login - ORDEN IMPORTANTE
            "backend_theme_explorer/static/src/css/o_call_chat_bot.css",
            'backend_theme_explorer/static/src/components/call_chat_bot_app/CallChatBotApp.js',
            "backend_theme_explorer/static/src/components/public/public_chatbot.js",
            "backend_theme_explorer/static/src/components/public/call_chat_bot_public.js",
            "backend_theme_explorer/static/src/debug_chatbot.js",  
        ],
        "web.assets_backend": [
            'backend_theme_explorer/static/src/css/o_call_chat_bot.css',
                  'backend_theme_explorer/static/src/components/public/call_chat_bot_public.js',
                  'backend_theme_explorer/static/src/components/call_chat_bot_app/CallChatBotApp.js',
                  'backend_theme_explorer/static/src/components/webclient/chatbot_injector.js',
                  'backend_theme_explorer/static/src/**/*.js',
                  'backend_theme_explorer/static/src/**/*.xml',
        ],
    },
    "installable": True,
    "license": "Other proprietary",
}