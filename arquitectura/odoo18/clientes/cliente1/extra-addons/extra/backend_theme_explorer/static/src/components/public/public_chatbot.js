/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { xml } from "@odoo/owl";

const PublicChatBotTemplate = xml`
<div class="o_public_chatbot fixed-bottom end-0 m-3" style="z-index: 1000;">
    <!-- Botón flotante -->
    <button class="btn btn-primary rounded-circle p-3" t-on-click="toggleChat" 
            style="width: 60px; height: 60px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
        <i class="fa fa-comments fa-lg"></i>
    </button>
    
    <!-- Ventana del chat -->
    <div t-if="state.open" class="card shadow-lg mt-2" 
         style="width: 350px; height: 500px; border-radius: 15px;">
        <!-- Header -->
        <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center" 
             style="border-radius: 15px 15px 0 0;">
            <h6 class="mb-0">
                <i class="fa fa-robot me-2"></i>
                Asistente Virtual
            </h6>
            <button class="btn btn-sm btn-light" t-on-click="toggleChat">
                <i class="fa fa-times"></i>
            </button>
        </div>
        
        <!-- Área de mensajes -->
        <div class="card-body p-3 d-flex flex-column">
            <div class="flex-grow-1 overflow-auto mb-3">
                <div class="alert alert-info text-center">
                    <small>¡Hola! ¿En qué puedo ayudarte?</small>
                </div>
                <!-- Los mensajes irían aquí -->
            </div>
            
            <!-- Input para mensajes -->
            <div class="input-group">
                <input type="text" class="form-control" placeholder="Escribe tu mensaje..."
                       t-model="state.currentMessage"
                       t-on-keypress="handleKeypress"/>
                <button class="btn btn-primary" t-on-click="sendMessage">
                    <i class="fa fa-paper-plane"></i>
                </button>
            </div>
        </div>
    </div>
</div>
`;

export class PublicChatBot extends Component {
    static template = PublicChatBotTemplate;
    
    setup() {
        this.state = useState({ 
            open: false,
            messages: [],
            currentMessage: ""
        });
    }

    toggleChat() {
        this.state.open = !this.state.open;
    }

    sendMessage() {
        if (this.state.currentMessage.trim()) {
            console.log("Mensaje enviado:", this.state.currentMessage);
            this.state.currentMessage = "";
        }
    }

    handleKeypress(ev) {
        if (ev.key === 'Enter') {
            this.sendMessage();
        }
    }
}