{
    'name': 'theme_jumpnjibe',
    'description': 'theme_jumpnjibe Custom theme for Hotel Jump N Jibe in Playa El Yaque',
    'category': 'Website/Theme',
    'version': '19.0.1.0.0',
    'author': 'Integraia',
    'summary': 'theme_jumpnjibe Theme for Hotel Jump N Jibe',
    'depends': ['website'],
    'data': [
        'security/ir.model.access.csv',
        'views/snippets.xml',
        'views/pages.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'theme_jumpnjibe/static/src/css/style.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}