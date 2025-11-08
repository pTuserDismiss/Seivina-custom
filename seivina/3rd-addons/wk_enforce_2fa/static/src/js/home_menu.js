/** @odoo-module **/

/* Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */

import { browser } from "@web/core/browser/browser";
import { TwoFAValidationPanel, mountComponent } from "@wk_enforce_2fa/js/twofa_panel";
import { UserMenu } from "@web/webclient/user_menu/user_menu";
import { patch } from "@web/core/utils/patch";
import { WebClient } from "@web/webclient/webclient";

patch(UserMenu.prototype, {
    setup() {
        super.setup(...arguments);
        let self = this;
        browser.addEventListener("hashchange", (ev) => {
            let modal_2fa = document.querySelector('.two_fa_validation_panel');
            let modal_2fa_len = document.querySelectorAll('.two_fa_validation_panel');
            if (modal_2fa === null || (modal_2fa !== null && !modal_2fa.classList.contains('show')) || modal_2fa_len.length === 0){
                mountComponent(TwoFAValidationPanel, document.body, { env: this.env});
            }
            if (modal_2fa !== null && !modal_2fa.classList.contains('show')) {
                self.env.bus.trigger("ENFORCE_2FA_ENABLE");
            }
        });
        browser.addEventListener("click", (ev) => {
            ev.stopPropagation();
            let modal_2fa = document.querySelector('.two_fa_validation_panel');
            let modal_2fa_len = document.querySelectorAll('.two_fa_validation_panel');
            if (modal_2fa === null || modal_2fa_len.length === 0){
                mountComponent(TwoFAValidationPanel, document.body, { env: this.env});
            }
            if (modal_2fa !== null && !modal_2fa.classList.contains('show')) {
                self.env.bus.trigger("ENFORCE_2FA_ENABLE");
            }
        });
    }
});

WebClient.components = {
    ...WebClient.components,
    TwoFAValidationPanel
}

patch(UserMenu.prototype, {
    checkIsLogout(element) {
        if (element.id === 'logout') {
            const route = "/web/session/logout";
            return () => {
                browser.location.href = route;
                sessionStorage.setItem('verification2FADone', 'logout');
            }
        }
        return element.callback;
    }
});
