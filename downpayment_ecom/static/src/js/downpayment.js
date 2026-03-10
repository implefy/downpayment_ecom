/** @odoo-module **/

import { rpc } from '@web/core/network/rpc';
import publicWidget from '@web/legacy/js/public/public_widget';

publicWidget.registry.DownpaymentToggle = publicWidget.Widget.extend({
    selector: '#downpayment_option',
    events: {
        'change input[name="payment_option"]': '_onPaymentOptionChange',
    },

    async _onPaymentOptionChange(ev) {
        const useDownpayment = ev.currentTarget.value === 'downpayment';
        const result = await rpc('/shop/downpayment/toggle', {
            use_downpayment: useDownpayment,
        });
        if (result.success) {
            // Reload the payment section to reflect the new amount
            window.location.reload();
        }
    },
});
