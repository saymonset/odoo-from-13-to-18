/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component, useState } from "@odoo/owl";
import { ItemCounter } from "@chat-bot-n8n-ia/components/ItemCounter/ItemCounter";
import { ChatBotWrapper } from "@chat-bot-n8n-ia/components/ChatBotWrapper/ChatBotWrapper";

const itemsInCart2 = [
    { productName: 'xxNintendo Switch 2', quantity: 1 },
    { productName: 'xxPro Controller', quantity: 2 },
    { productName: 'xxSuper Smash', quantity: 5 },
];

export class FirstStepsApp extends Component {
    static components = { ItemCounter, ChatBotWrapper };
    static template = "chat-bot-n8n-ia.FirstStepsApp";

    setup() {
        this.state = useState({
            itemsInCart2,
            chatWebhook: "https://n8n.jumpjibe.com/webhook/ea8c57a1-8e6d-4459-9c44-0b5add871f24/chat",
        });
    }
}

registry.category("actions").add("chat-bot-n8n-ia.FirstStepsApp", FirstStepsApp);
