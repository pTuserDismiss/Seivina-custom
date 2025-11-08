/** @odoo-module **/

/* Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */

import { WebsiteSale } from "@website_sale/js/website_sale";
import { session } from "@web/session";
import { browser } from "@web/core/browser/browser";
import { user } from "@web/core/user";

function preparePopup(qrCode, secret, obj) {
    let n = $(`
<div class="modal two_fa_validation_panel" tabindex="-1" role="dialog">
    <div class="modal-dialog" role="document">
        <div class="modal-content">
            <div class="modal-header text-center">
                <h6 class="modal-title w-100">Two Factor Authentication not enabled<br/>
                Kindly follow the below steps to enable Two Factor Authentication</h6>
            </div>
            <div class="modal-body">
                <div class="alert enforce-notify d-none" role="alert">
                </div>
                <div class="o_auth_totp_enable_2FA container mt-2">
                    <div class="mb-3 w-100">
                        <h5 class="fw-bold">Authenticator App Setup</h5>
                        <ul>
                            <div class="d-md-none d-block">
                                <li> Click on this link to open your authenticator app </li>
                            </div>
                            <li>
                                <div class="d-flex align-items-center flex-wrap">
                                    <span class="d-md-none d-block">Or install an authenticator app</span>
                                    <span class="d-none d-md-block">Install an authenticator app on your mobile device</span>
                                    <div class="d-block d-md-none">
                                        <a href="https://play.google.com/store/search?q=authenticator&amp;c=apps" class="mx-2" target="blank">
                                            <img alt="On Google Play" style="width: 24px;" src="/base_setup/static/src/img/logo_google_play.png">
                                        </a>
                                        <a href="http://appstore.com/2fa" class="mx-2" target="blank">
                                            <img alt="On Apple Store" style="width: 24px;" src="/base_setup/static/src/img/logo_apple_store.png">
                                        </a>
                                    </div>
                                </div>
                            </li>
                            <span class="text-muted">Popular ones include Authy, Google Authenticator or the Microsoft Authenticator.</span>
                            <li>Look for an "Add an account" button</li>
                            <li><span class="d-none d-md-block">When requested to do so, scan the barcode below</span><span class="d-block d-md-none">When requested to do so, copy the key below</span></li>
                        </ul>
                        <!-- Desktop version -->
                        <div class="text-center d-none d-md-block">
                            <img src="data:image/png;base64,${qrCode}" name="qrcode">
                            <h5 class="fw-bold">
                                <a data-bs-toggle="collapse" href="#collapseTotpSecret" role="button" aria-expanded="false" aria-controls="collapseTotpSecret">Cannot scan it?</a>
                            </h5>
                            <div class="collapse m-auto" id="collapseTotpSecret">
                                <div class="d-grid overflow-hidden tfa_secret">
                                    <span>${secret}</span>
                                    <button class="text-nowrap btn btn-sm btn-primary o_clipboard_button o_btn_char_copy tfa_secret_copy rounded-0" data="${secret}">
                                        <span class="fa fa-clipboard mx-1"></span>
                                        <span>Copy</span>
                                    </button>
                                </div>
                            </div>
                        </div>
                        <!-- Mobile Version -->
                        <div class="text-center d-block d-md-none">
                            <div class="d-grid overflow-hidden tfa_secret">
                                <span>${secret}</span>
                                <button class="text-nowrap btn btn-sm btn-primary tfa_secret_copy rounded-0" data="${secret}">
                                    <span class="fa fa-clipboard mx-1"></span><span>Copy</span>
                                </button>
                            </div>
                        </div>
                        <h5 class="fw-bold mt-2">Enter your six-digit code below</h5>
                        <div class="mt-2">
                            <label for="code" class="px-0 fw-bold">Verification Code</label>
                            <br>
                            <div class="o_field_widget o_required_modifier o_field_char o_field_highlight px-0 me-2">
                                <input class="o_input" name="code" id="code" type="number" autocomplete="off" maxlength="7" placeholder="e.g. 123456">
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-primary btn-verify">Verify</button>
            </div>
        </div>
    </div>
</div>
`);

    n.find('.btn-verify').click(async function (ev) {
        let code = n.find('#code').val();
        if (code === '' || code.length !== 6) {
            n.find('.enforce-notify').addClass('alert-danger');
            n.find('.enforce-notify').html("Please enter valid verification code.");
            n.find('.enforce-notify').removeClass('d-none');
            return true;
        } else {
            n.find('.enforce-notify').addClass('d-none');
        }
        code = parseInt(code);
        const response = await obj.orm.call(
            "res.users",
            "enable",
            [[user.userId], code, secret],
        );
        if (response.success) {
            n.find('.enforce-notify').addClass('alert-success');
            n.find('.enforce-notify').html(response.error);
            n.find('.enforce-notify').removeClass('d-none');
            n.modal('hide');
            session.tfa_enabled = true;
        } else {
            n.find('.enforce-notify').addClass('alert-danger');
            n.find('.enforce-notify').removeClass('d-none');
            n.find('.enforce-notify').html(response.error);
        }

    });
    n.find('.tfa_secret_copy').click(async function (ev) {
        let secret = $(ev.currentTarget).attr('data')
        try {
            await browser.navigator.clipboard.writeText(secret);
            $(ev.currentTarget).html(`<span class="fa fa-clipboard mx-1"></span><span>Copied</span>`)
        } catch (error) {
            return browser.console.warn(error);
        }
    })
    return n;
}

WebsiteSale.include({
    events: Object.assign({}, WebsiteSale.prototype.events || {}, {
        "click a[name='website_sale_main_button']": '_onClickEnforceCheckout',
    }),

    init: function () {
        this._super.apply(this, arguments);
        this.orm = this.bindService("orm");
    },

    _onClickEnforceCheckout: function (ev) {
        if (session.tfa_enforced && !session.tfa_enabled) {
            ev.stopImmediatePropagation();
            this.orm.call(
                "res.users",
                "generate_qrcode_tfa",
                [user.userId],
            ).then((user) => {
                if (user.tfa_enforced && !user.tfa_enabled) {
                    let popup = preparePopup(user.qr_code, user.secret, this);

                    $('#product_details').append(popup);
                    popup.modal({
                        backdrop: false
                    });
                    popup.modal('show');
                    return;
                }
            })
        } else {
            window.location = $(ev.currentTarget).data('href');
        }
    },

    _onClickSubmit: function (ev, forceSubmit) {
        if (session.tfa_enforced && !session.tfa_enabled) {
            ev.stopImmediatePropagation();
            this.orm.call(
                "res.users",
                "generate_qrcode_tfa",
                [user.userId],
            ).then((user) => {
                if (user.tfa_enforced && !user.tfa_enabled) {
                    let popup = preparePopup(user.qr_code, user.secret, this);

                    $('#product_details').append(popup);
                    popup.modal({
                        backdrop: false
                    });
                    popup.modal('show');
                    return;
                }
            })
        } else {
            this._super.apply(this, arguments);
        }
    },
});

$(document).ready(function () {
    if (window.location.pathname === '/web/login/totp/enforce') {
        $('.two_fa_validation_panel').modal({
            backdrop: false
        });
        $('.two_fa_validation_panel').modal('show');
        let n = $('.two_fa_validation_panel');
        n.find('.btn-verify').click(async function (ev) {
            let code = n.find('#code').val();
            if (code === '' || code.length !== 6) {
                n.find('.enforce-notify').addClass('alert-danger');
                n.find('.enforce-notify').html("Please enter valid verification code.");
                n.find('.enforce-notify').removeClass('d-none');
                return true;
            } else {
                n.find('.enforce-notify').addClass('d-none');
            }
            code = parseInt(code);
            n.find('#web_login_enforce').submit();
        });
        n.find('.tfa_secret_copy').click(async function (ev) {
            let secret = $(ev.currentTarget).attr('data');
            try {
                await browser.navigator.clipboard.writeText(secret);
                $(ev.currentTarget).html(`<span class="fa fa-clipboard mx-1"></span><span>Copied</span>`)
            } catch (error) {
                return browser.console.warn(error);
            }
        });
    };
});

