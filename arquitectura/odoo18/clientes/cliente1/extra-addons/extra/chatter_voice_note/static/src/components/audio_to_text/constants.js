/** @odoo-module **/
//TEST
// En path del webhook, se coloca test-audios para entorno de pruebas
  export const N8N_WEBHOOK_URL = "https://n8n.jumpjibe.com/webhook/test-audios";

// En path del webhook, se coloca audios para entorno de produccion
  //#  PRODUCCION
//export const N8N_WEBHOOK_URL = "https://n8n.jumpjibe.com/webhook/audios";

// CONFIGURACIÓN MÍNIMA Y COMPATIBLE
export const AUDIO_CONSTRAINTS = {
    audio: true
};

export const BUS_CHANNELS = {
    AUDIO_TEXT: 'audio_to_text_channel_1'
};