{
    'name': 'Conversión de Moneda en POS y Ventas',
    'summary': 'Conversión automática de moneda en Punto de Venta y Ventas',
    'version': '19.0.1.0.0',
    'category': 'Sales/Point of Sale',
    'author': 'Simon Alberto Rodriguez Pacheco',
    'website': 'https://github.com/simonrodriguezpacheco',
    'maintainer': 'Simon Alberto Rodriguez Pacheco',
    'license': 'LGPL-3',
    
    'depends': [
        'point_of_sale',
        'sale',
    ],
    
    'data': [
        'security/ir.model.access.csv',
        'views/test_test_views.xml',
    ],
    
    'assets': {
        'point_of_sale.assets': [
            'conver_pos_sales/static/src/**/*',
        ],
        'web.assets_backend': [
            'conver_pos_sales/static/src/**/*',
        ],
    },
    
    'application': True,
    'installable': True,
    'auto_install': False,
}