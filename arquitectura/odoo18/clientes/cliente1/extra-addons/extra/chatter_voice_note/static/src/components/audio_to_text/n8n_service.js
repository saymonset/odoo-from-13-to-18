/** @odoo-module **/
import { N8N_WEBHOOK_URL, BUS_CHANNELS } from "./constants";

export class N8NService {
    constructor(orm, notification, userService) {
        this.orm = orm;
        this.notification = notification;
        this.userService = userService;
    }

    async sendToN8N(audioNotes, contacts, resModel, resId) {
        try {
            const payload = await this.buildPayload(audioNotes, contacts, resModel, resId);
            await this.sendPayload(payload);
            return true;
        } catch (error) {
            this.handleSendError(error);
            return false;
        }
    }

    async buildPayload(audioNotes, contacts, resModel, resId) {
        const audios = audioNotes.length > 0 ? await this.getAudioData(audioNotes) : [];
        
        return {
            record_id: resId || null,
            model: resModel || null,
            audios,
            contacts: contacts,
            user_id: this.userService.userId,
            bus_channel: BUS_CHANNELS.AUDIO_TEXT
        };
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

        if (response.ok) {
            const noteCount = payload.audios.length;
            const contactCount = payload.contacts.length;
            this.notification.add(
                `Enviado: ${noteCount} audios, ${contactCount} contactos. Esperando respuesta...`,
                { type: "info" }
            );
        } else {
            throw new Error(`HTTP ${response.status}: ${await response.text()}`);
        }
    }

    handleSendError(error) {
        console.error("Error enviando a n8n:", error);
        const errorMessage = error.message.includes('HTTP') 
            ? `Error al enviar: ${error.message}`
            : "Error de conexión al enviar.";
            
        this.notification.add(errorMessage, { type: "danger" });
    }
}