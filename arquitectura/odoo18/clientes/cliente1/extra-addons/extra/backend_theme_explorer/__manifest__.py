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
        "web.assets_frontend": [
            ('include', 'web._assets_bootstrap_frontend'),
            "backend_theme_explorer/static/fonts/poppins.css",
            "backend_theme_explorer/static/src/scss/login.scss",
             'chat-bot-n8n-ia/static/src/**/*.js',
             'chat-bot-n8n-ia/static/src/**/*.xml',
        ],
         'web.assets_backend': [
                  'chat-bot-n8n-ia/static/src/**/*.js',
                  'chat-bot-n8n-ia/static/src/**/*.xml',
              ],
    },
    "installable": True,
    "license": "Other proprietary",
}