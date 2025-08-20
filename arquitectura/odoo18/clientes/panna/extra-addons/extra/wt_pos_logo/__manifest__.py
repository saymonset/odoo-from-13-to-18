# Copyright (C) Wisenetic Technologies.
# -*- coding: utf-8 -*-
{
    "name": "POS Logo & Screen Saver",
    "summary": "Enhanced POS Branding: Custom Logos, Hide Option, and Screen Saver Backgrounds.[POS Receipt Custom Logo, Point of Sale Logo Management, Add Company Logo in POS, Customize POS Receipt Header, Custom Branding for POS System, POS Logo Display Settings, Change POS Session Logo,POS Screen Saver Background Image, POS Terminal Branding Module,POS Interface Logo Settings, Replace Odoo Logo in POS, Point of Sale Custom Background, Personalize POS System Look, POS Logo and Branding Options, Odoo POS Screen Customizer, Logo and Background Manager for POS, Flexible POS Logo Customization Tool]",
    "description": """
        POS Logo & Screen Saver
        =============
        Give your Odoo POS a professional, branded look:
        - Replace default Odoo POS logo with your **Company Logo**.
        - Option to upload and use a **Custom Logo**.
        - Option to **Hide the POS Logo**.
        - Change the **POS Screen Saver background** image easily from POS configuration.
        - Clean, optimized, and well-documented code.

        Features:
        ---------
        - POS Logo Options: **Company Logo**, **Custom Logo**, or **No Logo**
        - Custom POS screen saver background
        - Fully integrated with POS configuration
        - Clean and lightweight implementation

    """,
    "author": "Wisenetic",
    "website": "https://www.wisenetic.com",
    "support": "info@wisenetic.com",
    "category": "Sales/Point of Sale",
    "version": "18.0.0.0.1",
    "depends": ["point_of_sale"],
    "data": ["views/res_config_settings_views.xml"],
    "images": ["static/description/banner.gif"],
    "assets": {
        "point_of_sale._assets_pos": [
            "wt_pos_logo/static/src/**/*",
        ]
    },
    "installable": True,
    "auto_install": False,
    "application": True,
    "license": "OPL-1",
    "price": "7.00",
    "currency": "USD",
}
