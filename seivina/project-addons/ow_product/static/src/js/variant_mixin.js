import VariantMixin from "@website_sale/js/sale_variant_mixin";

var oldFunctionDisableInput = VariantMixin._disableInput;

VariantMixin._disableInput = function ($parent) {
    oldFunctionDisableInput.apply(this, arguments);
    $parent.find('input.css_not_available, option.css_not_available').prop('disabled', true);
};

var oldFunctionCheckExclusions = VariantMixin._checkExclusions;

VariantMixin._checkExclusions = function ($parent) {
    $parent.find('input.css_not_available, option.css_not_available').prop('disabled', false);
    oldFunctionCheckExclusions.apply(this, arguments);
};