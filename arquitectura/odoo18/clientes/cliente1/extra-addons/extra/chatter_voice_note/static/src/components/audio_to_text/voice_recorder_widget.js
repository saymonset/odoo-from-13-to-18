/** @odoo-module **/

import { registry } from "@web/core/registry";
import { VoiceRecorder } from "./voice_recorder";

// Registrar el componente como widget
const voiceRecorderWidget = {
    component: VoiceRecorder,
    extractProps: ({ attrs }) => {
        return {
            resModel: attrs.res_model,
            resId: attrs.res_id,
            context: attrs.context,
        };
    },
};

// Registrar en el sistema de widgets
registry.category("view_widgets").add("voice_recorder", voiceRecorderWidget);