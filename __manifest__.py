# -*- coding: utf-8 -*-
{
    'license': 'LGPL-3',

    'name': "MyModule",

    'summary': "First custom module for odoo",

    'description': """
	Application test pour odoo 
    """,

    'author': "Saber Mahjoub",
    'website': "https://www.odoo.com",
    
    'installable': True,
    'application' : True,
    'auto_install': False,

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': [        
        'base',
        'hr',
        'mail' 
    ],

    'external_dependencies': {
        'python': ['qrcode'],
    },

    # always loaded
    'data': [
        'security/reunion_security.xml',
        'security/salle_security.xml',
        'security/ir.model.access.csv',
        'views/reunion.xml',
        'views/salle.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    "assets": {
        "web.assets_backend": [
            "static/src/js/copy_url_widget.js",
            "static/src/xml/copy_url_widget.xml",
        ],
    },
}

