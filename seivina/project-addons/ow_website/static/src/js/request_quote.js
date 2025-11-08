odoo.define('ow_website.request_quote', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.registry.RequestQuoteModal = publicWidget.Widget.extend({
        selector: '#requestQuoteModal',
        events: {
            'submit #requestQuoteForm': '_onSubmit',
            'click .btn-close': '_onClose',
        },

        /**
         * @override
         */
        start: function () {
            this._super.apply(this, arguments);
            this._setupFormValidation();
        },

        /**
         * Setup form validation
         */
        _setupFormValidation: function () {
            var self = this;
            var form = this.$('#requestQuoteForm')[0];
            
            if (form) {
                form.addEventListener('submit', function (event) {
                    if (!form.checkValidity()) {
                        event.preventDefault();
                        event.stopPropagation();
                    }
                    form.classList.add('was-validated');
                });
            }
        },

        /**
         * Handle form submission
         */
        _onSubmit: function (event) {
            var self = this;
            var form = event.currentTarget;
            var submitBtn = form.querySelector('button[type="submit"]');
            
            // Disable submit button to prevent double submission
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fa fa-spinner fa-spin me-2"></i>Submitting...';
            }

            // Form will submit normally to the /shop/request_quote endpoint
            // The controller will handle the submission and redirect back to cart
        },

        /**
         * Handle modal close
         */
        _onClose: function (event) {
            var form = this.$('#requestQuoteForm')[0];
            if (form) {
                form.reset();
                form.classList.remove('was-validated');
            }
        },
    });

    return publicWidget.registry.RequestQuoteModal;
});
