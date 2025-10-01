/** @odoo-module **/
import { registry } from "@web/core/registry";
import { ItemCounter } from "@chat-bot-n8n-ia/components/ItemCounter/ItemCounter";
import { Component, onMounted, onWillStart, useState } from "@odoo/owl";
import { loadJS, loadCSS } from "@web/core/assets";
 

 

 const itemsInCart2 = [
    { productName: 'xxNintendo Switch 2', quantity: 1 },
    { productName: 'xxPro Controller', quantity: 2 },
    { productName: 'xxSuper Smash', quantity: 5 },
];
export class FirstStepsApp extends Component {
    static components = {  ItemCounter};
    static template = "chat-bot-n8n-ia.FirstStepsApp";
    static props = {};

    setup() {
        this.state = useState({
            loaded: false,
            error: null
        });
        
        onWillStart(async () => {
            await this.loadDependencies();
            this.initializeChat();
        });
        
        onMounted(() => {
            
        });
        
        this.state.itemsInCart2 = itemsInCart2;
    }


    async loadDependencies() {
        try {
            // Cargar CSS
            await loadCSS('https://cdn.jsdelivr.net/npm/@n8n/chat/dist/style.css');
            
            // Cargar el módulo JavaScript
            await this.loadChatModule();
            
            this.state.loaded = true;
        } catch (error) {
            console.error('Error loading chatbot dependencies:', error);
            this.state.error = error.message;
        }
    }

     
    async loadChatModule() {
    try {
            const module = await import('https://cdn.jsdelivr.net/npm/@n8n/chat/dist/chat.bundle.es.js');
            if (module.createChat) {
                window.n8nCreateChat = module.createChat;
            } else {
                throw new Error('createChat not found in module');
            }
        } catch (err) {
            console.error('Error importing chat module:', err);
            throw err;
        }
    }


     initializeChat() {
        try {
            if (window.n8nCreateChat) {
                window.n8nCreateChat({
                    webhookUrl: 'https://n8n.jumpjibe.com/webhook/4eef5bde-1509-4240-9b8f-9723e26d723f/chat',
                    // Puedes agregar más opciones aquí según la documentación de n8n/chat
                });
            } else {
                throw new Error('n8nCreateChat function not available');
            }
        } catch (error) {
            console.error('Error initializing chat:', error);
            this.state.error = error.message;
        }
    }
}
// Register as a field widget
registry
  .category("actions")
  .add("chat-bot-n8n-ia.FirstStepsApp", FirstStepsApp);