/** @odoo-module **/
//TEST
// el n8n es /personal/lead/unisa/voz-to-text/tests-voz-to-text
// En path del webhook, se coloca test-audios para entorno de pruebas
  export const N8N_WEBHOOK_URL = "https://n8n.jumpjibe.com/webhook/test-audios";

// En path del webhook, se coloca audios para entorno de produccion
  //#  PRODUCCION
  //el n8n es personal/lead/unisa/voz-to-text/prod-voz-to-text
//export const N8N_WEBHOOK_URL = "https://n8n.jumpjibe.com/webhook/audios";

// CONFIGURACIÓN MÍNIMA Y COMPATIBLE
export const AUDIO_CONSTRAINTS = {
    audio: true
};

export const BUS_CHANNELS = {
    AUDIO_TEXT: 'audio_to_text_channel_1'
};