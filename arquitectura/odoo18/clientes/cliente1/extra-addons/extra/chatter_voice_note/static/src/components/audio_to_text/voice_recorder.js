/** @odoo-module **/
import { Component, useState, onWillStart, onWillUnmount } from "@odoo/owl";
import { useService, useBus } from "@web/core/utils/hooks";

// Constantes
const N8N_WEBHOOK_URL = "https://n8n.jumpjibe.com/webhook-test/audios";
const AUDIO_CONSTRAINTS = {
    audio: {
        channelCount: 1,
        sampleRate: 16000,
        sampleSize: 16
    }
};

export class VoiceRecorder extends Component {
    static template = "chatter_voice_note.VoiceRecorder";

    setup() {
        this.initServices();
        this.state = useState(this.getInitialState());
        this.setupEventListeners();
        
        onWillStart(() => this.onComponentStart());
        onWillUnmount(() => this.onComponentUnmount());
    }

    // === INICIALIZACIÓN ===
    initServices() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.busService = this.getServiceSafely("bus_service");
        this.userService = this.getServiceSafely("user") || { userId: null };
        
        this.currentStream = null;
    }

    getInitialState() {
        return {
            recording: false,
            uploading: false,
            mediaRecorder: null,
            notes: [],
            error: null,
            isSending: false,
            searchTerm: '',
            availableContacts: [],
            selectedContacts: [],
            final_message: '',
            answer_ia: '',
            loading_response: false,
        };
    }

    setupEventListeners() {
        this.handleAudioResponse = this.handleAudioResponse.bind(this);
        useBus(this.env.bus, "AUDIO_TEXT_RESPONSE", this.handleAudioResponse);
    }

    // === MANEJO DEL CICLO DE VIDA ===
    async onComponentStart() {
        this.state.loading_response = false;
        if (this.busService?.addChannel) {
            this.busService.addChannel("audio_to_text_channel_1");
        }
    }

    onComponentUnmount() {
        this.cleanupStream();
        if (this.busService?.leave) {
            this.busService.leave("audio_to_text_channel_1");
        }
    }

    // === SERVICIOS ===
    getServiceSafely(serviceName) {
        try {
            return useService(serviceName);
        } catch (error) {
            console.warn(`Servicio ${serviceName} no disponible:`, error.message);
            return null;
        }
    }

    // === MANEJO DE RESPUESTAS DE AUDIO ===
    handleAudioResponse(ev) {
        const payload = ev.detail;
        console.log("Evento AUDIO_TEXT_RESPONSE recibido:", payload);
        
        this.updateResponseState(payload);
        this.resetAfterResponse();
        
        if (payload.final_message) {
            this.notification.add(
                "Respuesta de audio recibida y procesada", 
                { type: "success" }
            );
        }
    }

    updateResponseState(payload) {
        if (payload.final_message) {
            this.state.final_message = payload.final_message;
        }
        if (payload.answer_ia) {
            this.state.answer_ia = payload.answer_ia;
        }
    }

    resetAfterResponse() {
        this.state.loading_response = false;
        this.state.notes = [];
        this.state.selectedContacts = [];
    }

    // === GESTIÓN DE CONTACTOS ===
    addContact(contact) {
        if (!this.state.selectedContacts.some(c => c.id === contact.id)) {
            this.state.selectedContacts.push(contact);
        }
        this.clearSearch();
    }

    removeContact(contactId) {
        this.state.selectedContacts = this.state.selectedContacts.filter(c => c.id !== contactId);
    }

    clearSearch() {
        this.state.searchTerm = '';
        this.state.availableContacts = [];
    }

    async searchContacts() {
        if (this.state.searchTerm.length < 2) {
            this.state.availableContacts = [];
            return;
        }
        
        try {
            const contacts = await this.orm.searchRead(
                "res.partner",
                [["name", "ilike", this.state.searchTerm]],
                ["name", "email", "phone"],
                { limit: 20 }
            );
            this.state.availableContacts = contacts;
        } catch (error) {
            console.error("Error buscando contactos:", error);
            this.state.availableContacts = [];
        }
    }

    // === GRABACIÓN DE AUDIO ===
    async toggleRecording() {
        if (this.state.recording) {
            this.stopRecording();
        } else {
            await this.startRecording();
        }
    }

    async startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia(AUDIO_CONSTRAINTS);
            this.setupMediaRecorder(stream);
            this.state.recording = true;
            this.state.error = null;
        } catch (err) {
            this.handleRecordingError(err);
        }
    }

    setupMediaRecorder(stream) {
        this.currentStream = stream;
        const recorder = new MediaRecorder(stream);
        const chunks = [];

        recorder.ondataavailable = (e) => {
            if (e.data.size > 0) chunks.push(e.data);
        };
        
        recorder.onstop = () => this.handleRecordingStop(chunks);
        recorder.start();
        this.state.mediaRecorder = recorder;
    }

    stopRecording() {
        if (this.state.mediaRecorder) {
            this.state.mediaRecorder.stop();
        }
        this.state.recording = false;
    }

    async handleRecordingStop(chunks) {
        this.cleanupStream();
        
        const blob = new Blob(chunks, { type: "audio/webm" });
        await this.createAudioNote(blob);
    }

    cleanupStream() {
        if (this.currentStream) {
            this.currentStream.getTracks().forEach(track => track.stop());
            this.currentStream = null;
        }
    }

    handleRecordingError(err) {
        console.error("Error accediendo al micrófono:", err);
        this.state.error = `Micrófono no disponible: ${err.message}`;
        this.state.recording = false;
    }

    // === GESTIÓN DE NOTAS DE AUDIO ===
    async createAudioNote(blob) {
        const url = URL.createObjectURL(blob);
        const name = `voice_note_${new Date().toISOString()}.webm`;
        const tempId = this.generateTempId();

        const newNote = {
            id: null,
            tempId,
            name,
            url,
            uploading: true,
            error: null
        };

        this.state.notes.push(newNote);
        await this.uploadAudio(blob, name, tempId);
    }

    generateTempId() {
        return `temp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    async uploadAudio(blob, name, tempId) {
        const noteIndex = this.state.notes.findIndex(n => n.tempId === tempId);
        if (noteIndex === -1) return;

        try {
            const base64 = await this.blobToBase64(blob);
            const attachmentId = await this.createAttachment(name, base64);
            
            this.updateNoteAfterUpload(noteIndex, tempId, attachmentId);
        } catch (err) {
            this.handleUploadError(noteIndex, tempId, err);
        }
    }

    blobToBase64(blob) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result.split(",")[1]);
            reader.onerror = () => reject(new Error("Error leyendo el archivo de audio"));
            reader.readAsDataURL(blob);
        });
    }

    async createAttachment(name, base64Data) {
        const [attachmentId] = await this.orm.create("ir.attachment", [{
            name,
            datas: base64Data,
            mimetype: "audio/webm",
            type: "binary",
            res_model: this.props.resModel || null,
            res_id: this.props.resId || null,
        }]);
        return attachmentId;
    }

    updateNoteAfterUpload(noteIndex, tempId, attachmentId) {
        if (this.state.notes[noteIndex]?.tempId === tempId) {
            this.state.notes[noteIndex].id = attachmentId;
            this.state.notes[noteIndex].uploading = false;
            delete this.state.notes[noteIndex].tempId;
        }
    }

    handleUploadError(noteIndex, tempId, err) {
        console.error("Error subiendo audio:", err);
        const errorMsg = err.data?.message || "Error al subir el audio";
        
        if (this.state.notes[noteIndex]?.tempId === tempId) {
            this.state.notes[noteIndex].error = errorMsg;
            this.state.notes[noteIndex].uploading = false;
        }
    }

    async deleteNote(noteId) {
        if (!confirm("¿Eliminar esta nota de voz permanentemente?")) {
            return;
        }
        
        try {
            if (noteId) {
                await this.orm.unlink("ir.attachment", [noteId]);
            }
            this.state.notes = this.state.notes.filter(n => n.id !== noteId);
        } catch (err) {
            console.error("Error eliminando nota:", err);
            this.state.error = "No se pudo eliminar la nota.";
            this.notification.add("Error al eliminar la nota", { type: "danger" });
        }
    }

    get sortedNotes() {
        return [...this.state.notes].sort((a, b) => (b.id || 0) - (a.id || 0));
    }

    // === ENVÍO A N8N ===
    async sendToN8N() {
        const notesToSend = this.state.notes.filter(n => n.id);

        if (notesToSend.length === 0 && this.state.selectedContacts.length === 0) {
            this.notification.add("No hay datos para enviar.", { type: "warning" });
            return;
        }

        this.prepareForSending();

        try {
            const payload = await this.buildPayload(notesToSend);
            await this.sendPayload(payload);
        } catch (error) {
            this.handleSendError(error);
        } finally {
            this.state.isSending = false;
        }
    }

    prepareForSending() {
        this.state.isSending = true;
        this.state.loading_response = true;
        this.state.final_message = '';
        this.state.answer_ia = '';
    }

    async buildPayload(notesToSend) {
        const audios = notesToSend.length > 0 ? await this.getAudioData(notesToSend) : [];
        
        return {
            record_id: this.props.resId || null,
            model: this.props.resModel || null,
            audios,
            contacts: this.state.selectedContacts.map(contact => ({
                id: contact.id,
                name: contact.name,
                email: contact.email || '',
                phone: contact.phone || '',
            })),
            user_id: this.userService.userId,
            bus_channel: "audio_to_text_channel_1"
        };
    }

    async getAudioData(notesToSend) {
        const attachmentIds = notesToSend.map(n => n.id);
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
        this.state.loading_response = false;
        
        const errorMessage = error.message.includes('HTTP') 
            ? `Error al enviar: ${error.message}`
            : "Error de conexión al enviar.";
            
        this.notification.add(errorMessage, { type: "danger" });
    }
}