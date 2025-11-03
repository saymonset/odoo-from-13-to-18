/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { Component } from "@odoo/owl";
import { VoiceRecorder } from "./voice_recorder";

export class Audio_to_text extends Component {
    static template = "chatter_voice_note.Audio_to_text";
    static components = { Layout, VoiceRecorder };

    setup() {
        // NO HAGAS NADA AQUÍ → el entorno se hereda solo
    }
}

<<<<<<< HEAD
registry.category("actions").add("chatter_voice_note.audio_to_text", Audio_to_text);
=======
// Registrar el servicio
registry.category("actions").add("chatter_voice_note.audio_to_text", Audio_to_text);
>>>>>>> audio_to_text_bus
