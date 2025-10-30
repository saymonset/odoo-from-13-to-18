/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillUnmount, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class VoiceRecorder extends Component {
    setup() {
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

        this.orm = useService("orm");
        this.busService = useService("bus_service");
        // Escuchar canal
        this.busService.addChannel("audio_to_text_channel");
        this.busService.addEventListener("notification", this.onNewResponse);

        onWillUnmount(() => {
            this.busService.deleteChannel("audio_to_text_channel");
            this.busService.removeEventListener("notification", this.onNewResponse);
        });

        onWillStart(() => {
            this.state.final_message = '';
            this.state.answer_ia = '';
            this.state.loading_response = false;
        });
        // Indicar que se está esperando respuesta
        this.state.loading_response = true;
    }

    onNewResponse = (notifications) => {
        for (const { type, payload } of notifications) {
            if (type === "new_response" && payload.final_message !== undefined) {
                console.log("✅ Recibido:", payload);
                this.state.final_message = payload.final_message || '';
                this.state.answer_ia = payload.answer_ia || '';
                this.state.loading_response = false;

                // Notificación opcional
                this.env.services.notification.add("Respuesta de IA recibida", {
                    type: "success",
                });
            }
        }
    };

    // === MÉTODOS DE CONTACTOS ===
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

    // === NOTAS ===
    get sortedNotes() {
        return [...this.state.notes].sort((a, b) => (b.id || 0) - (a.id || 0));

    }
    async deleteNote(noteId) {
        if (!noteId) {
            this.state.notes = this.state.notes.filter(note => note.id !== noteId);
            return;
        }

        if (!confirm("¿Eliminar esta nota de voz permanentemente?")) return;

        try {
            await this.orm.unlink("ir.attachment", [noteId]);
            this.state.notes = this.state.notes.filter(note => note.id !== noteId);
        } catch (error) {
            console.error("Error al eliminar:", error);
            this.state.error = "No se pudo eliminar la nota.";
        }
    }

    // === BÚSQUEDA ===
    async searchContacts() {
        if (this.state.searchTerm.length < 2) {
            this.state.availableContacts = [];
            return;
        }
        try {
            const domain = [['name', 'ilike', this.state.searchTerm]];
            const fields = ['name', 'email', 'phone'];
            const contacts = await this.orm.searchRead('res.partner', domain, fields, { limit: 20 });
            this.state.availableContacts = contacts;
        } catch (error) {
            console.error("Error buscando contactos:", error);
            this.state.error = "Error al buscar contactos.";
        }
    }

    // === GRABACIÓN ===
    async toggleRecording() {
        if (this.state.recording) {
            this.state.mediaRecorder.stop();
            this.state.recording = false;
            return;
        }

        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const recorder = new MediaRecorder(stream);
            const chunks = [];

            recorder.ondataavailable = e => e.data.size && chunks.push(e.data);
            recorder.onstop = async () => {
                const blob = new Blob(chunks, { type: "audio/webm" });
                const url = URL.createObjectURL(blob);
                const name = `voice_note_${new Date().toISOString()}.webm`;
                const tempId = Date.now();

                this.state.notes.push({
                    id: null,
                    tempId,
                    name,
                    url,
                    uploading: true,
                    error: null,
                });

                const noteIndex = this.state.notes.findIndex(n => n.tempId === tempId);
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

                        if (noteIndex !== -1) {
                            this.state.notes[noteIndex].id = attachmentId;
                            this.state.notes[noteIndex].uploading = false;
                            delete this.state.notes[noteIndex].tempId;
                        }
                    } catch (rpcError) {
                        const msg = rpcError.data?.message || rpcError.message || "Error al subir";
                        this.state.notes[noteIndex].error = msg;
                        this.state.notes[noteIndex].uploading = false;
                    }
                };

                reader.readAsDataURL(blob);
            };

            recorder.start();
            this.state.mediaRecorder = recorder;
            this.state.recording = true;
            this.state.error = null;
        } catch (err) {
            this.state.error = `Micrófono no disponible: ${err.message}`;
        }
    }

    // === ENVÍO A N8N ===
    async sendToN8N() {
        const N8N_WEBHOOK_URL = "https://n8n.jumpjibe.com/webhook-test/audios";
        const notesToSend = this.state.notes.filter(note => note.id);

        if (notesToSend.length === 0 && this.state.selectedContacts.length === 0) {
            alert("No hay datos para enviar.");
            return;
        }

        this.state.isSending = true;
        this.state.loading_response = true;  // ← AÑADE ESTO

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
            };

            const response = await fetch(N8N_WEBHOOK_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });

            if (response.ok) {
                alert(`Enviado: ${notesToSend.length} audios, ${this.state.selectedContacts.length} contactos`);
                this.state.notes = [];
                this.state.selectedContacts = [];

   
            } else {
                const err = await response.text();
                alert(`Error n8n: ${response.status} - ${err.substring(0, 100)}`);
            }
        } catch (error) {
            console.error("Error de red:", error);
            alert("Error de conexión al enviar.");
        } finally {
            this.state.isSending = false;
        }
    }

   
}

VoiceRecorder.template = "chatter_voice_note.VoiceRecorder";
registry.category("actions").add("chatter_voice_note.audio_to_text", VoiceRecorder);