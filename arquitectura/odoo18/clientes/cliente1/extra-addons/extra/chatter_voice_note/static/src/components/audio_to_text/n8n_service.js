/** @odoo-module **/
import { N8N_WEBHOOK_URL } from "./constants";

export class N8NService {
    constructor(orm, notification) {
        this.orm = orm;
        this.notification = notification;
    }

    /**
     * ENVÍA TODO A n8n COMO JSON + BASE64
     * → n8n recibe audios sin usar binary → NO null
     */
    async sendToN8N(notesToSend, contactsToSend, resModel, resId, requestId) {
        // === CONVERTIR BLOBS A BASE64 ===
        const audiosBase64 = await Promise.all(
            notesToSend.map(async (note) => {
                if (!note.data || note.data.size === 0) {
                    console.warn("Audio vacío, omitido");
                    return null;
                }

                try {
                    const base64 = await this.blobToBase64(note.data);
                    return {
                        filename: note.filename,
                        data: base64,           // ← base64 string
                        mimetype: "audio/webm"
                    };
                } catch (err) {
                    console.error("Error convirtiendo blob a base64:", err);
                    return null;
                }
            })
        );

        // Filtrar audios válidos
        const validAudios = audiosBase64.filter(a => a !== null);

        // === PAYLOAD JSON ===
        const payload = {
            audios: validAudios,
            contacts: contactsToSend,
            res_model: resModel || null,
            res_id: resId || null,
            request_id: requestId,
            callback_url: `${window.location.origin}/chatter_voice_note/audio_to_text?request_id=${requestId}`
        };

        console.log("Enviando a n8n:", {
            audios: validAudios.length,
            contacts: contactsToSend.length,
            request_id: requestId
        });

        try {
            const response = await fetch(N8N_WEBHOOK_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP ${response.status}: ${errorText}`);
            }

            const data = await response.json();
            this.notification.add(
                `Enviado: ${validAudios.length} audio(s), ${contactsToSend.length} contacto(s)`,
                { type: "success" }
            );

            return data;

        } catch (error) {
            console.error("Error enviando a n8n:", error);
            this.notification.add(`Error: ${error.message}`, { type: "danger" });
            throw error;
        }
    }

    /**
     * UTILIDAD: Convierte Blob → Base64 (sin "data:audio/webm;base64,")
     */
    blobToBase64(blob) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => {
                const base64String = reader.result.split(',')[1];
                resolve(base64String);
            };
            reader.onerror = () => reject(new Error("Error leyendo blob"));
            reader.readAsDataURL(blob);
        });
    }
}