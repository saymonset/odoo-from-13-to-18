{
    "name": "Delivery Orders Report",
    "version": "1.0",
    "description": "Delivery Orders Report",
    "summary": "Delivery Orders Report",
    "author": "MyCompany",
    "license": "LGPL-3",
    "category": "sale",
    "depends": [
        "base",
        "sale_management",
        "stock",
        "product",
        "web",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/profit_margin_views.xml",
        "report/header_template.xml",
        "report/header_delivery_order.xml",
        "report/header_delivery_category.xml",
        "report/average_sales_report.xml",
        "report/category_report.xml",
        "report/order_report.xml",
        "report/profit_margin_report.xml",
        "wizard/wizard_average_sales.xml",
        "wizard/wizard_delivery_order.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "delivery_orders_report/static/src/components/ColumnProgress/ColumnProgress.js",  # Ruta a tu archivo JS
            "delivery_orders_report/static/src/**/*.js",  # Ruta a tu archivo JS
            "delivery_orders_report/static/src/**/*.xml",  # Ruta a tu archivo JS
        ],
        "web.assets_qweb": [
            "delivery_orders_report/static/src/**/*.js",  # Ruta a tus archivos QWeb
            "delivery_orders_report/static/src/**/*.xml",  # Ruta a tus archivos QWeb
        ],
    },
}
