/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { Component, onWillStart } from "@odoo/owl";
import { useState } from "@odoo/owl";
import { VoiceRecorder } from "./voice_recorder";

export class AudioToText extends Component {
    static template = "chatter_voice_note.Audio_to_text";
    static components = { Layout, VoiceRecorder };

    setup() {
        this.state = useState({ params: {} });
        onWillStart(this.extractParameters.bind(this));
    }

    extractParameters() {
        const actionService = this.env.services.action;
        const controller = actionService.currentController;

        if (controller && controller.action) {
            const action = controller.action;
            const context = action.context || {};

            if (context.active_model && context.active_id) {
                // NUEVO OBJETO → fuerza reactividad
                this.state.params = {
                    resModel: context.active_model,
                    resId: context.active_id,
                    customRequestPrefix: `diagnosis_${context.active_id}`,
                };
                console.log("Params from action.context:", this.state.params);
                return;
            }
        }

        // NUEVO OBJETO vacío
        this.state.params = {};
    }
}

registry.category("actions").add("chatter_voice_note.audio_to_text", AudioToText);