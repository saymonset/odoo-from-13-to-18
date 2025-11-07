/** @odoo-module **/
import { Component, useState, onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { ContactManager } from "./contact_manager";
import { AudioRecorder } from "./audio_recorder";
import { AudioNoteManager } from "./audio_note_manager";
import { N8NService } from "./n8n_service";

export class VoiceRecorder extends Component {
    static template = "chatter_voice_note.VoiceRecorder";

    setup() {
        console.log("🔧 Setup VoiceRecorder - Versión Simplificada");
        
        this.initServices();
        this.initManagers();
        
        // ESTADO SIMPLIFICADO
        this.state = useState({
            recording: false,
            isSending: false,
            final_message: '',
            answer_ia: '',
            debugInfo: 'Sistema listo',
            error: null
        });
        
        this.currentRequestId = null;

        onWillUnmount(() => this.cleanup());
    }

    initServices() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        console.log("✅ Servicios cargados");
    }

    initManagers() {
        this.contactManager = new ContactManager(this.orm);
        this.audioRecorder = new AudioRecorder();
        this.audioNoteManager = new AudioNoteManager(this.orm, this.notification);
        this.n8nService = new N8NService(this.orm, this.notification);
    }

    // 🔥 MÉTODOS DE MANEJO DE EVENTOS SIMPLIFICADOS
    onSearchInput(ev) {
        this.contactManager.state.searchTerm = ev.target.value;
        this.contactManager.searchContacts();
    }

    onAddContact(ev) {
        const contactId = parseInt(ev.currentTarget.dataset.contactId);
        const contact = this.contactManager.state.availableContacts.find(c => c.id === contactId);
        if (contact) {
            this.contactManager.addContact(contact);
        }
    }

    onRemoveContact(ev) {
        const contactId = parseInt(ev.currentTarget.dataset.contactId);
        this.contactManager.removeContact(contactId);
    }

    deleteNote(ev) {
        const noteId = parseInt(ev.currentTarget.dataset.noteId);
        this.audioNoteManager.deleteNote(noteId);
    }

 async sendToN8N() {
    const notes = this.audioNoteManager.getNotesForSending();
    const contacts = this.contactManager.getSelectedContacts();

    if (notes.length === 0) {
        this.notification.add("Graba un audio primero", { type: "warning" });
        return;
    }

    this.currentRequestId = `req_${Date.now()}`;
    this.state.isSending = true;

    try {
        await this.n8nService.sendToN8N(
            notes,
            contacts,
            this.props.resModel,
            this.props.resId,
            this.currentRequestId
        );
    } catch (err) {
        console.error("Error envío:", err);
    } finally {
        this.state.isSending = false;
    }
}

    // 🔥 VERIFICAR RESPUESTA MANUALMENTE
    async checkResponse() {
        if (!this.currentRequestId) {
            this.notification.add("No hay solicitud activa para verificar", { type: "info" });
            return;
        }

        this.state.debugInfo = 'Verificando respuesta...';
        
        try {
            const response = await this.tryControllerCall(this.currentRequestId);
            
            if (response && response.final_message) {
                console.log("✅ RESPUESTA ENCONTRADA:", response);
                this.processResponse(response);
            } else {
                this.state.debugInfo = 'Respuesta aún no disponible';
                this.notification.add("La respuesta aún no está disponible. Intenta más tarde.", { 
                    type: "info" 
                });
            }
            
        } catch (error) {
            console.error("❌ Error verificando respuesta:", error);
            this.state.debugInfo = `Error: ${error.message}`;
            this.notification.add(`Error al verificar: ${error.message}`, { type: "danger" });
        }
    }

    // 🔥 LLAMADA DIRECTA AL CONTROLADOR
    async tryControllerCall(requestId) {
        try {
            console.log("🔍 Buscando respuesta via controlador para:", requestId);
            
            const payload = {
                request_id: requestId
            };

            const response = await fetch('/chatter_voice_note/get_response', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: JSON.stringify(payload)
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log("📥 Respuesta recibida:", data);
                return data;
            } else {
                console.log("⚠️ Controlador respondió con error:", response.status);
                return null;
            }
            
        } catch (error) {
            console.log("⚠️ Controlador no disponible:", error.message);
            return null;
        }
    }

    // 🔥 PROCESAR RESPUESTA
    processResponse(payload) {
        this.state.final_message = String(payload.final_message);
        this.state.answer_ia = String(payload.answer_ia || '');
        this.state.debugInfo = 'Procesamiento completado ✓';
        this.state.error = null;
        
        this.notification.add(
            `✅ Procesamiento completado: ${payload.final_message.substring(0, 40)}...`,
            { type: "success" }
        );
        
        // Auto-reset después de éxito
        setTimeout(() => {
            this.resetInterface();
        }, 10000);
    }

    cleanup() {
        if (this.state.recording) {
            this.audioRecorder.cleanup();
        }
    }

    // 🔥 RESET DE INTERFAZ
    resetInterface() {
        this.audioNoteManager.reset();
        this.contactManager.reset();
        this.currentRequestId = null;
        this.state.final_message = '';
        this.state.answer_ia = '';
        this.state.debugInfo = 'Sistema listo para nueva consulta';
        this.state.error = null;
    }

    // 🔥 MÉTODOS EXISTENTES
    async toggleRecording() {
        if (this.state.recording) {
            await this.stopRecording();
        } else {
            await this.startRecording();
        }
    }

    async startRecording() {
        try {
            await this.audioRecorder.startRecording();
            this.state.recording = true;
            this.state.error = null;
        } catch (err) {
            this.state.error = err.message;
            this.state.recording = false;
        }
    }

    // ... resto del código igual ...

async stopRecording() {
    try {
        const blob = await this.audioRecorder.stopRecording();
        this.state.recording = false;

        if (blob && blob.size > 0) {
            const url = URL.createObjectURL(blob);
            await this.audioNoteManager.createAudioNote({ blob, url });
        }
    } catch (err) {
        this.state.error = err.message;
    }
}

    get sortedNotes() {
        return this.audioNoteManager.sortedNotes;
    }
}