/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component, useState } from "@odoo/owl";

 
export class CallChatBotApp extends Component {
    static components = { };
    static template = "call_chat_bot.CallChatBot";

     setup() {
        this.state = useState({ open: false });
    }

    toggleChat() {
        this.state.open = !this.state.open;
    }
}

registry.category("actions").add("call_chat_bot.CallChatBot", CallChatBotApp);
