/** @odoo-module **/
import { Component, useState, onWillStart, onWillUnmount } from "@odoo/owl";
import { useService, useBus } from "@web/core/utils/hooks";

export class VoiceRecorder extends Component {
    static template = "chatter_voice_note.VoiceRecorder";

    setup() {
        this.orm = useService("orm");
        this.bus = useService("bus_service");
        this.notification = useService("notification");

        this.currentStream = null; // ← NUEVO: Para gestionar el stream del micrófono

        this.state = useState({
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
        });

        onWillStart(async () => {
            // Inicialización si es necesaria
            this.state.loading_response = false; // ← Mejor inicializar como false
        });

        
    
        // Limpieza manual del canal
        onWillUnmount(() => {
    
        });
    }

    

    

    // === CONTACTOS ===
    addContact(contact) {
        if (!this.state.selectedContacts.some(c => c.id === contact.id)) {
            this.state.selectedContacts.push(contact);
        }
        this.state.searchTerm = '';
        this.state.availableContacts = [];
    }

    removeContact(contactId) {
        this.state.selectedContacts = this.state.selectedContacts.filter(c => c.id !== contactId);
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

    // === GRABACIÓN - CORREGIDO ===
    async toggleRecording() {
        if (this.state.recording) {
            this.state.mediaRecorder.stop();
            this.state.recording = false;
            return;
        }

        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    channelCount: 1,
                    sampleRate: 16000,
                    sampleSize: 16
                } 
            });
            
            this.currentStream = stream; // Guardar referencia para limpiar después
            const recorder = new MediaRecorder(stream);
            const chunks = [];

            recorder.ondataavailable = (e) => {
                if (e.data.size > 0) {
                    chunks.push(e.data);
                }
            };
            
            recorder.onstop = async () => {
                // ✅ CORREGIDO: Liberar recursos del micrófono
                stream.getTracks().forEach(track => track.stop());
                this.currentStream = null;
                
                const blob = new Blob(chunks, { type: "audio/webm" });
                const url = URL.createObjectURL(blob);
                const name = `voice_note_${new Date().toISOString()}.webm`;
                const tempId = `temp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

                this.state.notes.push({ 
                    id: null, 
                    tempId, 
                    name, 
                    url, 
                    uploading: true, 
                    error: null 
                });
                
                const noteIndex = this.state.notes.findIndex(n => n.tempId === tempId);
                await this.uploadAudio(blob, name, noteIndex, tempId);
            };

            recorder.start();
            this.state.mediaRecorder = recorder;
            this.state.recording = true;
            this.state.error = null;
        } catch (err) {
            console.error("Error accediendo al micrófono:", err);
            this.state.error = `Micrófono no disponible: ${err.message}`;
            this.state.recording = false;
        }
    }

    // ✅ NUEVO: Método separado para subir audio
    async uploadAudio(blob, name, noteIndex, tempId) {
        const reader = new FileReader();
        reader.onload = async () => {
            const base64 = reader.result.split(",")[1];
            try {
                const [attachmentId] = await this.orm.create("ir.attachment", [{
                    name,
                    datas: base64,
                    mimetype: "audio/webm",
                    type: "binary",
                    res_model: this.props.resModel || null,
                    res_id: this.props.resId || null,
                }]);
                
                if (noteIndex !== -1 && this.state.notes[noteIndex]?.tempId === tempId) {
                    this.state.notes[noteIndex].id = attachmentId;
                    this.state.notes[noteIndex].uploading = false;
                    delete this.state.notes[noteIndex].tempId;
                }
            } catch (err) {
                console.error("Error subiendo audio:", err);
                const msg = err.data?.message || "Error al subir el audio";
                if (noteIndex !== -1 && this.state.notes[noteIndex]?.tempId === tempId) {
                    this.state.notes[noteIndex].error = msg;
                    this.state.notes[noteIndex].uploading = false;
                }
            }
        };
        reader.onerror = () => {
            if (noteIndex !== -1 && this.state.notes[noteIndex]?.tempId === tempId) {
                this.state.notes[noteIndex].error = "Error leyendo el archivo de audio";
                this.state.notes[noteIndex].uploading = false;
            }
        };
        reader.readAsDataURL(blob);
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
        const N8N_WEBHOOK_URL = "https://n8n.jumpjibe.com/webhook-test/audios";
        const notesToSend = this.state.notes.filter(n => n.id);

        if (notesToSend.length === 0 && this.state.selectedContacts.length === 0) {
            this.notification.add("No hay datos para enviar.", { type: "warning" });
            return;
        }

        this.state.isSending = true;
        this.state.loading_response = true;

        try {
            let audios = [];
            if (notesToSend.length > 0) {
                const attachmentIds = notesToSend.map(n => n.id);
                const attachments = await this.orm.read("ir.attachment", attachmentIds, ["name", "datas", "mimetype"]);
                audios = attachments.map(a => ({
                    filename: a.name,
                    mimetype: a.mimetype,
                    data: a.datas,
                }));
            }

            const payload = {
                record_id: this.props.resId || null,
                model: this.props.resModel || null,
                audios,
                contacts: this.state.selectedContacts.map(c => ({
                    id: c.id,
                    name: c.name,
                    email: c.email || '',
                    phone: c.phone || '',
                })),
                user_id: this.userId,
            };

            const response = await fetch(N8N_WEBHOOK_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });

            if (response.ok) {
                this.notification.add(
                    `Enviado: ${notesToSend.length} audios, ${this.state.selectedContacts.length} contactos`,
                    { type: "success" }
                );
                this.state.notes = [];
                this.state.selectedContacts = [];
            } else {
                const errorText = await response.text();
                console.error("Error n8n:", response.status, errorText);
                this.notification.add(
                    `Error al enviar: ${response.status}`,
                    { type: "danger" }
                );
                this.state.loading_response = false;
            }
        } catch (error) {
            console.error("Error de red:", error);
            this.notification.add("Error de conexión al enviar.", { type: "danger" });
            this.state.loading_response = false;
        } finally {
            this.state.isSending = false;
        }
    }
}