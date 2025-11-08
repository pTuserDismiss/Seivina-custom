# -*- coding: utf-8 -*-
#################################################################################
# Author: Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
    "name": "Odoo Enforce Two-Factor Authentication | 2FA",
    "summary": """Odoo Enforce Two-Factor Authentication module enhances account security by implementing Two-factor authentication (2FA) for public users, reducing unauthorized access and ensuring data confidentiality through unique passcodes and a pop-up window.""",
    "category": "Tools",
    "version": "1.0.0",
    "sequence": 1,
    "author": "Webkul Software Pvt. Ltd.",
    "website": "https://store.webkul.com/odoo-enforce-2fa.html",
    "license":  "Other proprietary",
    "description": """Odoo Enforce 2FA module allows administrators to enforce Two-factor authentication (2FA) for public users, enhancing account security and preventing unauthorized access. This involves keeping a secret inside an authenticator and exchanging a code while attempting to log in using a QR code. 2FA minimizes the risks of hacked passwords and ensures data confidentiality. After entering the username and password, a pop-up window requests a 2FA PIN to activate 2FA on every page the user opens or reloads, ensuring the security and confidentiality of data.""",
    "live_test_url": "http://odoodemo.webkul.in/?module=wk_enforce_2fa",
    "depends": [
        "base",
        "web",
        "auth_totp",
        "website_sale",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/res_config_settings_views.xml",
        "views/res_users_views.xml",
        "views/template.xml",
        "wizard/enforce_action_wizard_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "wk_enforce_2fa/static/src/xml/twofa_panel.xml",
            "wk_enforce_2fa/static/src/js/twofa_panel.js",
            "wk_enforce_2fa/static/src/js/home_menu.js",
            "wk_enforce_2fa/static/src/scss/twofa_panel.scss",
        ],
        'web.assets_frontend': [
            "wk_enforce_2fa/static/src/scss/twofa_panel.scss",
            "wk_enforce_2fa/static/src/js/twofa_panel.js",
            "wk_enforce_2fa/static/src/js/twofa_panel_frontend.js",
        ]
    },
    "images": ["static/description/banner.png"],
    "installable": True,
    "application": True,
    "auto_install": False,
    "price": 75,
    "currency": "USD",
    "pre_init_hook": "pre_init_check",
}
