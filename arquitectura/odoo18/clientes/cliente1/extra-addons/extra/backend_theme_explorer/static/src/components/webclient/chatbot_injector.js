/** @odoo-module **/

import { registry } from "@web/core/registry";
import { CallChatBotApp } from "@backend_theme_explorer/components/call_chat_bot_app/CallChatBotApp";

registry.category("main_components").add("call_chat_bot.CallChatBot", {
    Component: CallChatBotApp,
    props: {},
});
