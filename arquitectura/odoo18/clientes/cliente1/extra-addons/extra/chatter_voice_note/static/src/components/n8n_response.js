/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
export class N8NResponse extends Component {
    static template = "chatter_voice_note.N8NResponse";
    static props = {
        final_message: { type: String, optional: true },
        answer_ia: { type: String, optional: true },
        loading_response: { type: Boolean },
    };
}
registry.category("components").add("chatter_voice_note.N8NResponse", N8NResponse);
