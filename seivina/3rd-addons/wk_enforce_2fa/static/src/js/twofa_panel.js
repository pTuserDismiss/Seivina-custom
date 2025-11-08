/** @odoo-module **/

/* Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */


const { Component, xml, onMounted, useState, useRef, onWillStart } = owl;
import { session } from "@web/session";
import { useBus, useService } from "@web/core/utils/hooks";
import { makeEnv, startServices } from "@web/env";
import { App, EventBus } from "@odoo/owl";
import { getTemplate } from "@web/core/templates";
import { _t } from "@web/core/l10n/translation";
import { browser } from "@web/core/browser/browser";
import { user } from "@web/core/user";

/**
 * 2FA Validation panel
 *
 * @extends Component
 */
export class TwoFAValidationPanel extends Component {
    static template = xml`
        <div
            class="two_fa_validation_panel modal fade"
            role="dialog" 
            data-bs-backdrop="static" 
            data-bs-keyboard="false"
            tabindex="-1"
            style="z-index:1200;"
            t-ref="tfa_panel"
            >
            <div class="modal-dialog" role="document">
                <div class="modal-content">
                    <div class="modal-header text-center">
                        <h5 class="modal-title w-100">
                            <b>
                                Two Factor Authentication not enabled <br/>Kindly follow the below steps to enable Two Factor Authentication
                            </b>
                        </h5>
                    </div>
                    <div t-if="state.errorMessage !== ''" t-attf-class="alert alert-{{!state.error ? 'success':'danger'}}" role="alert">
                        <t t-esc="state.errorMessage"/>
                    </div>
                    <div class="o_auth_totp_enable_2FA container mt-2">
                        <div class="mb-3 w-100">
                            <h3 class="fw-bold">Authenticator App Setup</h3>
                            <ul>
                                <div class="d-md-none d-block">
                                    <li>
                                        Click on this link to open your authenticator app
                                    </li>
                                </div>
                                <li>
                                    <div class="d-flex align-items-center flex-wrap">
                                        <span class="d-md-none d-block">Or install an authenticator app</span>
                                        <span class="d-none d-md-block">Install an authenticator app on your mobile device</span>
                                        <div class="d-block d-md-none">
                                            <a href="https://play.google.com/store/search?q=authenticator&amp;c=apps" class="mx-2" target="blank">
                                                <img alt="On Google Play" style="width: 24px;" src="/base_setup/static/src/img/logo_google_play.png"/>
                                            </a>
                                            <a href="http://appstore.com/2fa" class="mx-2" target="blank">
                                                <img alt="On Apple Store" style="width: 24px;" src="/base_setup/static/src/img/logo_apple_store.png"/>
                                            </a>
                                        </div>
                                    </div>
                                </li>

                                <span class="text-muted">Popular ones include Authy, Google Authenticator or the Microsoft Authenticator.</span>
                                <li>Look for an "Add an account" button</li>
                                <li>
                                    <span class="d-none d-md-block">When requested to do so, scan the barcode below</span>
                                    <span class="d-block d-md-none">When requested to do so, copy the key below</span>
                                </li>
                            </ul>
                            <!-- Desktop version -->
                            <div class="text-center d-none d-md-block">
                                <img src="" name="qrcode" t-ref="qrcode"/>

                                <h3 class="fw-bold"><a data-bs-toggle="collapse"
                                   href="#collapseTotpSecret" role="button" aria-expanded="false"
                                   aria-controls="collapseTotpSecret">Cannot scan it?</a></h3>
                                <div class="collapse m-auto" id="collapseTotpSecret">
                                    <div class="d-grid overflow-hidden tfa_secret">
                                        <span t-ref="secret"></span>
                                        <button class="text-nowrap btn btn-sm btn-primary o_clipboard_button o_btn_char_copy rounded-0" t-on-click="(e) => this.cpSecretCp(false)">
                                            <span class="fa fa-clipboard mx-1"></span><span>Copy</span>
                                        </button>
                                    </div>
                                </div>
                            </div>

                            <!-- Mobile Version -->
                            <div class="text-center d-block d-md-none">
                                <div class="d-grid overflow-hidden tfa_secret">
                                    <span t-ref="secretm"></span>
                                    <button class="text-nowrap btn btn-sm btn-primary rounded-0" t-on-click="(e) => this.cpSecretCp(true)">
                                        <span class="fa fa-clipboard mx-1"></span><span>Copy</span>
                                    </button>
                                </div>
                            </div>

                            <h3 class="fw-bold mt-2">Enter your six-digit code below</h3>
                            <div class="mt-2">
                                <label for="code" class="px-0 fw-bold">Verification Code</label>
                                <br/>
                                <div class="o_field_widget o_required_modifier o_field_char o_field_highlight px-0 me-2">
                                    <input class="o_input" name="code" id="code" type="number" autocomplete="off" maxlength="7" placeholder="e.g. 123456" t-ref="verfCode" t-on-keyup="keyupVRF"/>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-primary" t-on-click="_enableTFAClose">Verify</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    setup() {
        super.setup(...arguments);
        this.orm = useService("orm");
        let self = this;
        this.root = useRef('tfa_panel');
        this.secret = useRef('secret');
        this.secretm = useRef('secretm');
        this.qrcode = useRef('qrcode');
        this.code = useRef('verfCode');

        if (sessionStorage.getItem('verification2FADone') === 'logout') {
            sessionStorage.setItem('verification2FADone', false);
        }

        this.state = useState({
            enabledTFA: false,
            enforceTFA: false,
            verificationDone: true ? sessionStorage.getItem('verification2FADone') === 'true' : false,
            secret: false,
            qrCode: false,
            error: false,
            errorMessage: '',
        });

        onWillStart(async () => {
            const current_user = await this.orm.call(
                "res.users",
                "generate_qrcode_tfa",
                [user.userId],
            );
            self.state.enabledTFA = current_user.tfa_enabled;
            self.state.enforceTFA = current_user.tfa_enforced;
            self.state.qrCode = current_user.qr_code;
            self.state.secret = current_user.secret;
            if (!self.state.enabledTFA) {
                self.state.verificationDone = false;
            }
        });
        session.isTFAAvailable = true;
        onMounted(this.customMounted);

        useBus(this.env.bus, "ENFORCE_2FA_ENABLE", this.enforce2FAEnable);
    }

    customMounted() {
        if (this.state.enforceTFA) {
            if (!this.state.verificationDone && !this.state.enabledTFA) {
                this.qrcode.el.setAttribute('src', "data:image/png;base64," + this.state.qrCode);
                this.secret.el.innerHTML = this.state.secret;
                this.secretm.el.innerHTML = this.state.secret;
                let element = this.root.el;
                this.root.el.style = "pointer-events: auto;z-index: 12000;";
                element.style.display = 'block';
                element.classList.add('show')
            }
        }
    }

    async enforce2FAEnable() {     
        const current_user = await this.orm.call(
            "res.users",
            "generate_qrcode_tfa",
            [user.userId],
        );
        this.state.enabledTFA = current_user.tfa_enabled;
        this.state.qrCode = current_user.qr_code;
        this.state.secret = current_user.secret;
        if (!this.state.enabledTFA) {
            this.state.verificationDone = false;
        }
        this.customMounted();
    }

    async _enableTFAClose(ev) {
        let self = this;
        let code = self.code.el.value
        if (code === '' || code.length !== 6) {
            self.state.error = true;
            self.state.errorMessage = "Please enter valid verification code.";
            return true;
        }
        code = parseInt(code);
        if (!self.state.enabledTFA && self.state.enforceTFA) {
            const response = await this.orm.call(
                "res.users",
                "enable",
                [[user.userId], code, self.state.secret],
            );
            if (response.success) {
                self.state.error = false;
                self.state.errorMessage = response.error;
                sessionStorage.setItem('verification2FADone', true);
                self.state.verificationDone = true;
                self.root.el.style.display = 'none';
            } else {
                self.state.error = true;
                self.state.errorMessage = response.error;
                sessionStorage.setItem('verification2FADone', false);
                self.state.verificationDone = false;
            }
        } else {
            const response = await rpc.query({
                model: "res.users",
                method: "tfa_check",
                args: [[user.userId], code],
            });
            if (response.success) {
                self.state.error = false;
                self.state.errorMessage = response.error;
                sessionStorage.setItem('verification2FADone', true);
                self.state.verificationDone = true;
                self.root.el.style.display = 'none';
            } else {
                self.state.error = true;
                self.state.errorMessage = response.error;
                sessionStorage.setItem('verification2FADone', false);
                self.state.verificationDone = false;
            }

        }
        return true;
    }

    async keyupVRF(ev) {
        if (ev.keyCode === 13) {
            return await this._enableTFAClose(ev);
        }
        return true;
    }

    async cpSecretCp(mobile) {
        if (mobile) {
            if (this.secretm.el) {
                var secret = this.secretm.el.innerHTML;
            }
        } else {
            if (this.secret.el) {
                var secret = this.secret.el.innerHTML;
            }
        }
        if (secret) {
            try {
                await browser.navigator.clipboard.writeText(secret);
                this.secret.el.nextSibling.innerHTML = `<span class="fa fa-clipboard mx-1"></span><span>Copied</span>`;
            } catch (error) {
                return browser.console.warn(error);
            }
        }
    }
}

export async function mountComponent(component, target, appConfig = {}) {
    let { env } = appConfig;
    const isRoot = !env;
    if (isRoot) {
        env = await makeEnv();
        await startServices(env);
    }
    const app = new App(component, {
        env,
        getTemplate,
        dev: env.debug || session.test_mode,
        warnIfNoStaticProps: !session.test_mode,
        name: component.constructor.name,
        translatableAttributes: ["data-tooltip"],
        translateFn: _t,
        ...appConfig,
    });
    const root = await app.mount(target);
    if (isRoot) {
        odoo.__WOWL_DEBUG__ = { root };
    }
    return app;
}
