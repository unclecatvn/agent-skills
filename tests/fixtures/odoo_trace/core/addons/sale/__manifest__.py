{
    'name': 'Sales',
    'category': 'Sales/Sales',
    'depends': ['portal'],
    'data': [
        'security/sale_security.xml',
        'security/ir.model.access.csv',
        'data/sale_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sale/static/src/js/**/*',
            ('remove', 'sale/static/src/js/debug.js'),
            ('include', 'web._assets_helpers'),
        ],
    },
}
