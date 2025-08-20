{
    "name": "POS Advanced Hide Control Buttons",
    "summary": """POS Hide Control Buttons pos hide control buttons pos hide buttons pos access pos access manage pos control access pos hide actions pos hide customer selection pos hide note pos Hide Customer Button pos Internal Note Button pos Quotation/Order Button pos hide Quotation pos Hide Tax pos Hide Refund Button pos Hide Refund Hide General Note pos Hide Note pos Hide Customer Note pos Hide Pricelist Button pos Hide Cancel Order Button pos hide cancel pos access managment pos restrict pos hide buttons pos access rules pos user access pos access restrict pos retail access pos all in one access pos access manage pos manager validation pOS hide Features POS Access rights POS functionality customization User-specific POS features Customize POS buttons and features Streamline user workflows Restrict sensitive POS functions Enable/disable POS features based on user roles User-specific POS access rights pos user restriction pos access rights pos disable buttons pos hide pos hide show""",
    "description": """Advanced POS Hide Control Buttons""",
    "category": "Point of Sale",
    "version": "18.0",
    "depends": [
        "point_of_sale",
    ],
    "data": [
        "views/res_users_view.xml",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "pos_controlbuttons_access/static/src/xml/controlbutton.xml",
            "pos_controlbuttons_access/static/src/js/models.js",
        ]
    },
    "author": "Khaled Hassan",
    "website": "https://apps.odoo.com/apps/modules/browse?search=Khaled+hassan",
    "license": "OPL-1",
    "currency": "EUR",
    "price": "30",
    "images": ["static/description/main_screenshot.png"],
    "installable": True,
    "auto_install": False,
    "application": False,
}
