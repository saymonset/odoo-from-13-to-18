{
    'name': 'BCV Rate Update for Venezuela',
    'summary': 'Actualización automática de tasa BCV para Venezuela',
    'description': """
        Obtiene diariamente la tasa de cambio oficial del BCV y actualiza
        la moneda VES en Odoo.
    """,
    'version': '19.0.1.0.0',
    'category': 'Sales/Point of Sale',
    'author': 'Simon Alberto Rodriguez Pacheco',
    'website': 'https://github.com/simonrodriguezpacheco',
    'maintainer': 'Simon Alberto Rodriguez Pacheco',
    'license': 'LGPL-3',
    
    'depends': ['base', 'account'],
    'external_dependencies': {
        'python': ['requests', 'beautifulsoup4'],
    },
    
    'data': [
         'security/ir.model.access.csv',
         'data/cron_data.xml',
        'views/res_currency_views.xml',
    ],
    
    'assets': {
        'point_of_sale.assets': [
            'conver_pos_sales/static/src/**/*',
        ],
        'web.assets_backend': [
            'conver_pos_sales/static/src/**/*',
        ],
    },
    
    'application': False,
    'installable': True,
    'auto_install': False,
    'images': [
        'conver_pos_sales/static/description/icon.png'
        
    ],
}