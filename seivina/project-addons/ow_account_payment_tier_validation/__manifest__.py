{
    "name": "Oakworks - Account Payment Tier Validation",
    "summary": "Extends the functionality of Account Payment to "
    "support a tier validation process.",
    "version": "18.0.0.0.1",
    "category": "Accounts",
    "author": "Novobi, LLC",
    "website": "https://www.novobi.com",
    "license": "OPL-1",
    "application": False,
    "installable": True,
    "depends": ["account", "ow_base_tier_validation", "account_partner_deposit", "sale_partner_deposit"],
    "data": ["views/account_payment_view.xml"],
}
