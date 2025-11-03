/** @odoo-module **/

import { registry } from "@web/core/registry";

 const busService = {
    dependencies: ["bus_service"],
    
    start(env, { bus_service }) {
        // Suscribirse al canal público
        bus_service.addChannel("audio_to_text_channel_1");
        
        // Escuchar eventos específicos
        bus_service.addEventListener("notification", ({ detail: notifications }) => {
            for (const notification of notifications) {
                if (notification[0] === "audio_to_text_channel_1") {
                    const payload = notification[1];
                    if (payload.type === "audio_to_text_response") {
                        this.handleAudioTextResponse(payload.payload);
                    }
                }
            }
        });
        
        return {
            handleAudioTextResponse: (payload) => {
                console.log("Mensaje recibido del servidor:", payload);
                
                // Mostrar notificación
                if (payload.final_message) {
                    env.services.notification.add(payload.final_message, {
                        type: "info",
                        title: "Audio a Texto",
                    });
                }
                
                // Procesar la respuesta de IA
                if (payload.answer_ia) {
                    console.log("Respuesta IA:", payload.answer_ia);
                    // Aquí puedes emitir un evento personalizado o actualizar componentes
                    env.bus.trigger("AUDIO_TEXT_RESPONSE", payload);
                }
            }
        };
    },
};


export default busService;

registry.category("services").add("audio_text_bus_service", busService);