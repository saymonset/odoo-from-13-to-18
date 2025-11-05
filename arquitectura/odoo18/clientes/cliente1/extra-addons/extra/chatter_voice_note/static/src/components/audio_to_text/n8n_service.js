/** @odoo-module **/
import { N8N_WEBHOOK_URL, BUS_CHANNELS } from "./constants";
import { _t } from "@web/core/l10n/translation";

export class N8NService {
    constructor(orm, notification, userService) {
        this.orm = orm;
        this.notification = notification;
        this.userService = userService;
    }

     
 async sendToN8N(notes, contacts, finalMessage = null, answerIa = null, requestId = null) {
        console.log("📤 Iniciando envío a N8N...", { 
            requestId, 
            notesCount: notes.length, 
            contactsCount: contacts.length 
        });

        try {
            const result = await this.orm.call(
                'audio_to_text.use.case',
                'execute',
                [{
                    notes: notes,
                    contacts: contacts,
                    final_message: finalMessage,
                    answer_ia: answerIa,
                    request_id: requestId,
                    timestamp: new Date().toISOString()
                }]
            );

            console.log("✅ Respuesta del backend:", result);
            
            if (result.status === 'processing') {
                this.notification.add(
                    _t("✅ Procesamiento iniciado: ") + result.message,
                    { type: "info" }
                );
            }
            
            return result;

        } catch (error) {
            console.error("❌ Error en N8NService:", error);
            this.notification.add(
                _t("❌ Error al enviar datos: ") + error.message, 
                { type: "danger" }
            );
            throw error;
        }
    }
    
    async buildPayload(audioNotes, contacts, resModel, resId, requestId) {
        const audios = audioNotes.length > 0 ? await this.getAudioData(audioNotes) : [];
        
        const payload = {
            record_id: resId || null,
            model: resModel || null,
            audios,
            contacts: contacts,
            user_id: this.userService.userId,
            bus_channel: BUS_CHANNELS.AUDIO_TEXT
        };

        // Agregar request_id si está disponible
        if (requestId) {
            payload.request_id = requestId;
        }
        
        return payload;
    }

    async getAudioData(notes) {
        const attachmentIds = notes.map(n => n.id);
        const attachments = await this.orm.read(
            "ir.attachment", 
            attachmentIds, 
            ["name", "datas", "mimetype"]
        );
        
        return attachments.map(attachment => ({
            filename: attachment.name,
            mimetype: attachment.mimetype,
            data: attachment.datas,
        }));
    }

    async sendPayload(payload) {
        const response = await fetch(N8N_WEBHOOK_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${await response.text()}`);
        }

        const noteCount = payload.audios.length;
        const contactCount = payload.contacts.length;
        this.notification.add(
            `📤 Enviado: ${noteCount} audios, ${contactCount} contactos. Esperando respuesta...`,
            { type: "info" }
        );

        return response;
    }

    handleSendError(error) {
        let errorMessage = "Error al enviar";
        if (error.message.includes('HTTP')) {
            errorMessage = `Error del servidor: ${error.message}`;
        } else if (error.name === 'TypeError') {
            errorMessage = "Error de conexión. Verifica tu internet.";
        }
        
        this.notification.add(errorMessage, { type: "danger" });
    }
}