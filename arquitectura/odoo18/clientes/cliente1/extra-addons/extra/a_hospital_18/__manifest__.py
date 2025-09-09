# -*- coding: utf-8 -*-
{
    'name': 'A_hospital_18',
    'version': '1.0.0',
    'summary': """ A_hospital_18 Summary """,
    'author': '',
    'website': '',
    'category': '',
    'depends': ['base', 'web'],
    "data": [
        "security/a_hospital_groups.xml",
        "security/ir.model.access.csv",
        "views/a_hospital_specialty_views.xml",
        "views/a_hospital_menu_views.xml"
    ],
    'assets': {
              'web.assets_backend': [
                  'a_hospital_18/static/src/**/*'
              ],
          },
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
