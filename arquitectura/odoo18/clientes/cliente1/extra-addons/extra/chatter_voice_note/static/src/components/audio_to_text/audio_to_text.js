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

registry.category("actions").add("chatter_voice_note.audio_to_text", Audio_to_text);