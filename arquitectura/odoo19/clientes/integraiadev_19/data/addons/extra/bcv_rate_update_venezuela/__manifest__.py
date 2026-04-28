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
    
    'depends': [
        'base',
        'sale_management',
        'account',          # Contabilidad base
        'stock',            # Inventario
        'point_of_sale',
        'website_sale', 
        'payment',
         
    ],

    'external_dependencies': {
        'python': ['requests', 'beautifulsoup4'],
    },
    
    'data': [
        'security/ir.model.access.csv',
        'data/cron_data.xml',
        'data/res_bank_data.xml',  
        'views/res_currency_views.xml',
        'views/sale_order_tree_debug.xml',
        'views/sale_order_views.xml',
        'views/website_cart_usd.xml',
        'views/payment_attachment_templates.xml',
        'views/payment_provider_views.xml',
        # 'views/invoice_report_templates.xml',
    ],
    
    'assets': {
        'point_of_sale.assets': [
            'bcv_rate_update_venezuela/static/src/**/*',
        ],
        'web.assets_backend': [
            'bcv_rate_update_venezuela/static/src/**/*',
        ],
         "web.assets_frontend": [
            'bcv_rate_update_venezuela/static/src/css/payment_proof_component.css',
            'bcv_rate_update_venezuela/static/src/js/payment_proof_component.js',  
            'bcv_rate_update_venezuela/static/src/xml/payment_proof_component.xml'
            
        ],
    },
    
    'application': False,
    'installable': True,
    'auto_install': False,
    'images': [
        'bcv_rate_update_venezuela/static/description/icon.png'
    ],
}