/** @odoo-module **/

import { patch } from '@web/core/utils/patch';
import {
    ProductConfiguratorDialog
} from '@sale/js/product_configurator_dialog/product_configurator_dialog';

patch(ProductConfiguratorDialog.prototype, {
    _isPossibleCombination(product) {
        return product.attribute_lines.every(ptal => {
            const selectedPtavIds = new Set(ptal.selected_attribute_value_ids);
            return !selectedPtavIds.has(0) && ptal.attribute_values
                .filter(ptav => selectedPtavIds.has(ptav.id))
                .every(ptav => !ptav.excluded);
        });
    },
    _checkExclusions(product) {
        const combination = this._getCombination(product);
        const exclusions = product.exclusions;
        const parentExclusions = product.parent_exclusions;
        const archivedCombinations = product.archived_combinations;
        const parentCombination = this._getParentsCombination(product);
        const childProducts = this._getChildProducts(product.product_tmpl_id)
        const ptavList = product.attribute_lines.flat().flatMap(ptal => ptal.attribute_values)
        ptavList.map(ptav => ptav.excluded = false); // Reset all the values

        if (exclusions) {
            if (combination.every(element => element === 0)){
                for(const ptav of ptavList) {
                    ptav.excluded = false;
                }
            }
            else{
                for(const ptavId of combination) {
                    if (ptavId!=0){
                        for(const excludedPtavId of exclusions[ptavId]) {
                                ptavList.find(ptav => ptav.id === excludedPtavId).excluded = true;
                        }
                    }
                }
            }
            
        }
        if (parentCombination) {
            for(const ptavId of parentCombination) {
                for(const excludedPtavId of (parentExclusions[ptavId]||[])) {
                    const ptav = ptavList.find(ptav => ptav.id === excludedPtavId);
                    if (ptav) {
                        ptav.excluded = true; // Assign only if the element exists
                    }
                }
            }
        }
        // if (archivedCombinations) {
        //     for(const excludedCombination of archivedCombinations) {
        //         const ptavCommon = excludedCombination.filter((ptav) => combination.includes(ptav));
        //         if (ptavCommon.length === combination.length) {
        //             if (combination.every(element => element === 0)){
        //                 for(const ptav of ptavList) {
        //                     ptav.excluded = false;
        //                 }
        //             }
        //             else{
        //                 for(const excludedPtavId of ptavCommon) {
        //                     if (excludedPtavId != 0){
        //                         ptavList.find(ptav => ptav.id === excludedPtavId).excluded = true;
        //                     }
        //                 }
        //             }
        //         } else if (ptavCommon.length === (combination.length - 1)) {
        //             // In this case we only need to disable the remaining ptav
        //             const disabledPtavId = excludedCombination.find(
        //                 (ptav) => !combination.includes(ptav)
        //             );
        //             const excludedPtav = ptavList.find(ptav => ptav.id === disabledPtavId)
        //             if (excludedPtav) {
        //                 excludedPtav.excluded = true;
        //             }
        //         }
        //     }
        // }
        for(const optionalProductTmpl of childProducts) {
            this._checkExclusions(optionalProductTmpl);
        }
    },
});
