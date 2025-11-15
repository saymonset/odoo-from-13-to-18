/** @odoo-module **/

import { patch } from 'web.utils';
import { useBus } from '@web/core/bus';
import { registry } from '@web/core/registry';
import { FormController } from '@web/views/form/form_controller';

patch(FormController.prototype, 'a_hospital.diagnosis_bus', {
    setup() {
        this._super();

        // Solo para Diagnosis
        if (this.modelName === 'a_hospital.diagnosis') {
            useBus('a_hospital_diagnosis_channel', this, this._onBusNotification);
        }
    },

    _onBusNotification(notification) {
        const recordId = notification[2];
        const channel = notification[1];
        const data = notification[3];

        if (channel === 'a_hospital_diagnosis_channel' && this.model.localId === recordId) {
            // Actualizamos description sin recargar la vista
            const field = this.renderer.getField('description');
            if (field) {
                field.props.value = data.description;
                field.willUpdateProps({ value: data.description });
            } else {
                // Forzar update si field no está disponible
                this.renderer.state.fields.description.value = data.description;
                this.renderer.update();
            }

        }
    },
});
