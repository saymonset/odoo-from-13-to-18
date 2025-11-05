/** @odoo-module **/
import { N8N_WEBHOOK_URL, BUS_CHANNELS } from "./constants";
import { _t } from "@web/core/l10n/translation";

export class N8NService {
    constructor(orm, notification) {
        this.orm = orm;
        this.notification = notification;
    }

    async sendToN8N(notes, contacts, resModel = null, resId = null, requestId = null) {
        console.log("📤 Iniciando envío a N8N...", { 
            requestId, 
            notesCount: notes.length, 
            contactsCount: contacts.length,
            resModel,
            resId
        });

        try {
            console.log("📤 Construyendo payload para N8N...");
            const payload = await this.buildPayload(notes, contacts, resModel, resId, requestId);
            console.log("📦 Payload construido:", payload);
            
            const response = await this.sendPayload(payload);
            console.log("✅ Envío a N8N completado");

            this.notification.add(
                _t("✅ Datos enviados a N8N. El modelo procesará la respuesta."),
                { type: "info" }
            );

            return {
                success: true,
                n8n_response: response,
                message: "Datos enviados correctamente a N8N"
            };

        } catch (error) {
            console.error("❌ Error en N8NService:", error);
            this.handleSendError(error);
            throw error;
        }
    }

    async buildPayload(audioNotes, contacts, resModel, resId, requestId) {
        const audios = audioNotes.length > 0 ? await this.getAudioData(audioNotes) : [];
        
        const payload = {
            record_id: resId || null,
            model: resModel || null,
            audios: audios,
            contacts: contacts,
            user_id: await this.getUserId(),
            bus_channel: BUS_CHANNELS.AUDIO_TEXT,
            request_id: requestId,
            timestamp: new Date().toISOString()
        };
        
        console.log("📦 Payload para N8N:", {
            audios_count: payload.audios.length,
            contacts_count: payload.contacts.length,
            request_id: payload.request_id,
            bus_channel: payload.bus_channel
        });
        
        return payload;
    }

    async getAudioData(notes) {
        try {
            const attachmentIds = notes.filter(n => n.id).map(n => n.id);
            
            if (attachmentIds.length === 0) {
                console.warn("⚠️ No hay attachments con ID para enviar");
                return [];
            }
            
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
        } catch (error) {
            console.error("❌ Error obteniendo datos de audio:", error);
            return [];
        }
    }

    async getUserId() {
        try {
            const user_id = await this.orm.call("res.users", "get_user_id", []);
            return user_id;
        } catch (error) {
            console.warn("⚠️ No se pudo obtener user_id:", error);
            return null;
        }
    }

    async sendPayload(payload) {
        console.log("🌐 Enviando payload a N8N...", {
            url: N8N_WEBHOOK_URL,
            payload_size: JSON.stringify(payload).length
        });

        const response = await fetch(N8N_WEBHOOK_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error("❌ Error en respuesta N8N:", response.status, errorText);
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }

        const responseData = await response.json();
        
        const noteCount = payload.audios.length;
        const contactCount = payload.contacts.length;
        this.notification.add(
            `📤 Enviado a N8N: ${noteCount} audios, ${contactCount} contactos`,
            { type: "info" }
        );

        return responseData;
    }

    handleSendError(error) {
        let errorMessage = "Error al enviar a N8N";
        if (error.message.includes('HTTP')) {
            errorMessage = `Error del servidor N8N: ${error.message}`;
        } else if (error.name === 'TypeError') {
            errorMessage = "Error de conexión. Verifica tu internet.";
        } else {
            errorMessage = `Error: ${error.message}`;
        }
        
        this.notification.add(errorMessage, { type: "danger" });
    }
}