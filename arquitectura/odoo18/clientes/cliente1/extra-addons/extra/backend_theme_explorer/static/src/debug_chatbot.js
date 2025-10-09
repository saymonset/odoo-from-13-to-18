/** @odoo-module **/
console.log("🟢 Debug: Archivo chatbot cargado");

document.addEventListener('DOMContentLoaded', function() {
    console.log("🟢 DOM completamente cargado");
    console.log("🟢 Contenedores encontrados:", document.querySelectorAll('.o_call_chat_bot_container').length);
    console.log("🟢 Ruta actual:", window.location.pathname);
});