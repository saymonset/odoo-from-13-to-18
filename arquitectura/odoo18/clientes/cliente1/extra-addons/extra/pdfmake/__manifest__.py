{
    'name': 'Pdfmake',
    'version': '1.0.0',
    'summary': 'Pdfmake Reports',
    'author': '',
    'website': '',
    'category': 'Tools',
    'depends': ['base', 'web','mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/layout_logo_only.xml',
        'views/pdf_printer_views.xml',
        'views/pdf_reports.xml', 
        'views/medical_report_views.xml', 
    ],
    'assets': {
        'web.assets_backend': [
            'pdfmake/static/src/fonts/*',
            # pdfmake desde CDN
            'https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.2.10/pdfmake.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.2.10/vfs_fonts.js',
            
          # Nuestros archivos JS - SOLO los esenciales
            'pdfmake/static/src/js/pdfmake_service.js',
            'pdfmake/static/src/js/simple_pdf_action.js',

        ],
    },
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}