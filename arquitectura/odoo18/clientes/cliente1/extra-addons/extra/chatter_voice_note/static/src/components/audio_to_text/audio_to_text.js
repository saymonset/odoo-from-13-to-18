import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { getDefaultConfig } from "@web/views/view";
import { Component, useSubEnv } from "@odoo/owl";
import { VoiceRecorder } from "./voice_recorder"; // Asegúrate de importar tu componente

export class Audio_to_text extends Component {
    static template = "chatter_voice_note.Audio_to_text";
    static components = { Layout, VoiceRecorder }; // Añade VoiceRecorder aquí

    setup() {
        useSubEnv({
            config: {
                ...getDefaultConfig(),
                ...this.env.config,
            },
        });
    }
}

// Registrar el servicio
registry.category("actions").add("chatter_voice_note.audio_to_text", Audio_to_text);
