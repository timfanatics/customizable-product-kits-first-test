# -*- coding: utf-8 -*-
{
    'name': "BOM to Sale Order",

    'summary': """
        Extract BOM of products""",

    'description': """
        Extract BOM of a product
    """,

    'author': "Mediod Consulting",
    'website': "https://www.mediodconsulting.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sale & Manufacturing',
    'version': '15.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['sale_management', 'mrp'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/sale_order.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
