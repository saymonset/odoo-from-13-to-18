/** @odoo-module **/
import { FormController } from "@web/views/form/form_controller";
import { patch } from "@web/core/utils/patch";

// Sintaxis CORRECTA para Odoo 18
patch(FormController.prototype, {
    // Método para abrir el grabador de voz existente
    async action_open_voice_recorder() {
        if (!this.model.root.resId) {
            // Si el registro no está guardado, guardarlo primero
            await this.model.root.save();
        }
        
        // Abrir el grabador de voz existente como acción de cliente
        return {
            'type': 'ir.actions.client',
            'tag': 'chatter_voice_note.audio_to_text',
            'target': 'new',
            'name': 'Grabador de Voz',
            'params': {
                'res_model': this.props.resModel,
                'res_id': this.model.root.resId,
            }
        };
    }
});