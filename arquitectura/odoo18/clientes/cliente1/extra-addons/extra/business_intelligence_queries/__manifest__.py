{
    'name': 'Business Intelligence Queries',
    'version': '18.0.1.0.0',
    'summary': 'Advanced SQL Query Builder and Custom Reports for Odoo 18',
    'author': 'Simon Alberto Rodriguez Pacheco',
    'website': 'https://tu-website.com',
    'category': 'Tools',
    'depends': ['base', 'sale', 'product', 'web'],  # Agregué 'sale'
    "data": [
       # "security/ir.model.access.csv",  # Si hay modelos
        "views/templates.xml",
    ],
    # ELIMINAR la sección 'controllers' o mover a data
    'assets': {
        'web.assets_backend': [
            'business_intelligence_queries/static/src/**/*'
        ],
    },
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}