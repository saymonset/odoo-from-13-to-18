/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { Component } from "@odoo/owl";
import { VoiceRecorder } from "./voice_recorder"; // Importación directa

export class AudioToText extends Component {
    static template = "chatter_voice_note.Audio_to_text";
    static components = { Layout, VoiceRecorder };

    setup() {
        // No necesitamos hacer nada aquí
    }
}

// Registrar la acción cliente
registry.category("actions").add("chatter_voice_note.audio_to_text", AudioToText);