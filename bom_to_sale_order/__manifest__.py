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
    'depends': ['base','web','mrp','sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/sale_order.xml',
        'report/sale_report_templates.xml',
        'views/sale_portal_templates.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'bom_to_sale_order/static/src/scss/so_lines.scss',
        ],
        'web.assets_frontend': [
            'bom_to_sale_order/static/src/scss/so_lines_portal.scss',
            'bom_to_sale_order/static/src/js/sale_portal_products.js',
        ],
    },
    # only loaded in demonstration mode
    'demo': [
    ],
    'application':True,
    'auto_install':False,
}
