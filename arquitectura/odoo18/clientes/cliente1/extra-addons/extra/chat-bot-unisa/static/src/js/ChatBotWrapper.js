/** @odoo-module **/
import { Component, useState, onWillStart } from "@odoo/owl";
import { loadCSS } from "@web/core/assets";
import { registry } from "@web/core/registry";

export class ChatBotWrapper extends Component {
    static template = "chat-bot-unisa.ChatBotWrapper";

    static props = {
        webhookUrl: { type: String, required: true },
    };

    setup() {
        this.state = useState({
            loaded: false,
            error: null,
        });

        onWillStart(async () => {
            try {
                await this.loadDependencies();
                this.initializeChat();
            } catch (err) {
                this.state.error = err.message;
                console.error('Error in setup:', err);
            }
        });
    }

    async loadDependencies() {
        try {
            // Cargar CSS de n8n
            await loadCSS('https://cdn.jsdelivr.net/npm/@n8n/chat/dist/style.css');
            console.log('✅ CSS n8n loaded');
            
            // ✅ CORREGIDO: Ruta absoluta del módulo
            await loadCSS('/chat-bot-unisa/static/src/css/chat-bot.css');
            console.log('✅ Custom CSS loaded');
        
            const module = await import('https://cdn.jsdelivr.net/npm/@n8n/chat/dist/chat.bundle.es.js');
            if (module.createChat) {
                window.n8nCreateChat = module.createChat;
                console.log('✅ n8n chat module loaded');
            } else {
                throw new Error('createChat not found in module');
            }
            this.state.loaded = true;
        } catch (err) {
            console.error('❌ Error loading dependencies:', err);
            throw err;
        }
    }

    initializeChat() {
        if (!window.n8nCreateChat) {
            throw new Error('n8nCreateChat function not available');
        }
        
        console.log('🚀 Initializing chat...');
        window.n8nCreateChat({
            webhookUrl: this.props.webhookUrl,
            initialMessages: [
                '¡Hola! 😊',
            ],
            i18n: {
                en: {
                    title: 'Bienvenido/a a UNISA, tu Unidad de Salud Integral.',
                    subtitle: "Inicia un chat. Estamos aquí para ayudarte 24/7.",
                    footer: '',
                    getStarted: 'Nueva Conversación',
                    inputPlaceholder: 'Por ejemplo: Precios,Servicios,Citas,Tarjeta de Salud o CREDIUNISA...',
                },
            },
            theme: {
                primaryColor: '#2C5AA0',
                secondaryColor: '#6B46C1',
            }
        });
        console.log('✅ Chat initialized');
    }
}

registry.category("public_components").add("ChatBotWrapper", ChatBotWrapper);