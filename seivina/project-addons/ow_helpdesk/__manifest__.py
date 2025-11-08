{
    'name': 'Oakworks - Helpdesk',
    "summary": "Customized module to manage helpdesk",
    "version": "18.0.0.0.0",
    'category': 'Services/Helpdesk',
    "author": "Novobi, LLC",
    "website": "https://www.novobi.com",
    "license": "OPL-1",
    "application": False,
    "installable": True,
    "depends": [
        "helpdesk",
        "worksheet",
        "ow_base",
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/helpdesk_security.xml',
        'views/helpdesk_ticket_type_views.xml',
        'views/helpdesk_ticket_views.xml',
        'views/worksheet_template_views.xml',
    ],
}
