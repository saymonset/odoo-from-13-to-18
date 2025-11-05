/** @odoo-module **/

//export const N8N_WEBHOOK_URL = "https://n8n.jumpjibe.com/webhook/audios";
export const N8N_WEBHOOK_URL = "https://n8n.jumpjibe.com/webhook-test/audios";

// Configuración mejorada para audio
export const AUDIO_CONSTRAINTS = {
    audio: {
        channelCount: 1,
        sampleRate: 16000,
        sampleSize: 16,
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true
    }
};

// Opciones alternativas para diferentes navegadores
export const MEDIA_RECORDER_OPTIONS = {
    mimeType: 'audio/webm; codecs=opus',
    audioBitsPerSecond: 128000
};

// Asegúrate de que el canal coincida exactamente con el del backend
export const BUS_CHANNELS = {
    AUDIO_TEXT: 'audio_to_text_channel_1'  // ✅ Mismo canal que el backend
};