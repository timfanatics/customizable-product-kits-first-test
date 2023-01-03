# -*- coding: utf-8 -*-
{
    'name': "Widget to expand/collapse One2Many Sections in Odoo",

    'summary': """
        Widget to expand/collapse One2Many Sections in Odoo.
        This widget will inherit existing one2many widget 'section_and_note_one2many' 
        and add a new functionality to expand and collapse sections in one2many field.
        This could be added to any existing one2many field or to any new one2many field with section_and_note_one2many widget
        """,

    'description': """
        Widget to expand/collapse One2Many Sections in Odoo.
        This widget will inherit existing one2many widget 'section_and_note_one2many' 
        and add a new functionality to expand and collapse sections in one2many field.
        This could be added to any existing one2many field or to any new one2many field with section_and_note_one2many widget
    """,

    'author': "Mediod Consulting",
    'website': "https://www.mediodconsulting.com",
    # for the full list
    'category': 'Sale & Manufacturing',
    'version': '16.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['sale_management','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/sale_order.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'md_widget_expand_collapse_sections/static/src/components/**/*.js',
            'md_widget_expand_collapse_sections/static/src/components/**/*.xml',
        ],
    },
    # only loaded in demonstration mode
    'demo': [
    ],

    'application': True,
    'price': 13.00,
    'currency': 'EUR',
    "images": ['static/description/Banner.png'],
}

