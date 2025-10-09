/** @odoo-module **/
import { mount } from "@odoo/owl";
import { PublicChatBot } from "./public_chatbot";

/**
 * Función que monta el chatbot en todos los contenedores existentes.
 * Se ejecuta después de que el DOM está listo.
 */
function initPublicChatBot() {
    const containers = document.querySelectorAll('.o_call_chat_bot_container');

    if (!containers.length) {
        console.warn("⚠️ No se encontró contenedor para el chatbot");
        return;
    }

    containers.forEach(container => {
        // Evitar montar varias veces
        if (!container.dataset.chatMounted) {
            mount(PublicChatBot, { target: container });
            container.dataset.chatMounted = "true";
            console.log("✅ ChatBot público montado en:", container);
        }
    });
}

// Montaje seguro al cargar DOM
document.addEventListener('DOMContentLoaded', () => {
    initPublicChatBot();

    // Opcional: si el DOM cambia dinámicamente (login page)
    const observer = new MutationObserver(() => initPublicChatBot());
    observer.observe(document.body, { childList: true, subtree: true });
});
