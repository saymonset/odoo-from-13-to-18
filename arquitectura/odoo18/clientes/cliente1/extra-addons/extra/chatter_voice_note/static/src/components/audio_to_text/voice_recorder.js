/** @odoo-module **/
import { Component, useState, onWillStart, onWillUnmount } from "@odoo/owl";
import { useService, useBus } from "@web/core/utils/hooks";
import { ContactManager } from "./contact_manager";
import { AudioRecorder } from "./audio_recorder";
import { AudioNoteManager } from "./audio_note_manager";
import { N8NService } from "./n8n_service";
import { BUS_CHANNELS } from "./constants";

export class VoiceRecorder extends Component {
    static template = "chatter_voice_note.VoiceRecorder";

    setup() {
        this.initServices();
        this.initManagers();
        this.state = useState(this.getInitialState());
        this.setupEventListeners();
        
        // Inicializar timeout de seguridad
        this.safetyTimeout = null;
        
        onWillStart(() => this.onComponentStart());
        onWillUnmount(() => this.onComponentUnmount());
    }

    initServices() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.busService = this.getServiceSafely("bus_service");
        this.userService = this.getServiceSafely("user") || { userId: null };
    }

    initManagers() {
        this.contactManager = new ContactManager(this.orm);
        this.audioRecorder = new AudioRecorder();
        this.audioNoteManager = new AudioNoteManager(this.orm, this.notification);
        this.n8nService = new N8NService(this.orm, this.notification, this.userService);
    }

    getInitialState() {
        return {
            recording: false,
            uploading: false,
            isSending: false,
            final_message: '',
            answer_ia: '',
            loading_response: false,
            error: null
        };
    }

    setupEventListeners() {
        this.handleAudioResponse = this.handleAudioResponse.bind(this);
        useBus(this.env.bus, "AUDIO_TEXT_RESPONSE", this.handleAudioResponse);
    }

    async onComponentStart() {
        this.state.loading_response = false;
        if (this.busService?.addChannel) {
            this.busService.addChannel(BUS_CHANNELS.AUDIO_TEXT);
        }
    }

    onComponentUnmount() {
        if (this.state.recording) {
            this.audioRecorder.cleanup();
        }
        if (this.busService?.leave) {
            this.busService.leave(BUS_CHANNELS.AUDIO_TEXT);
        }
        // Limpiar timeout al desmontar el componente
        if (this.safetyTimeout) {
            clearTimeout(this.safetyTimeout);
            this.safetyTimeout = null;
        }
    }

    getServiceSafely(serviceName) {
        try {
            return useService(serviceName);
        } catch (error) {
            console.warn(`Servicio ${serviceName} no disponible:`, error.message);
            return null;
        }
    }

    // === MANEJO DE RESPUESTAS DE AUDIO CON TIMEOUT ===
    handleAudioResponse(ev) {
        const payload = ev.detail;
        console.log("✅ Evento AUDIO_TEXT_RESPONSE recibido:", payload);
        
        // Limpiar timeout de seguridad
        if (this.safetyTimeout) {
            clearTimeout(this.safetyTimeout);
            this.safetyTimeout = null;
        }
        
        // PRIMERO reiniciar el estado de envío
        this.state.isSending = false;
        this.state.loading_response = false;
        
        // LUEGO actualizar con la respuesta
        this.updateResponseState(payload);
        
        // FINALMENTE resetear managers
        this.audioNoteManager.reset();
        this.contactManager.reset();
        
        if (payload.final_message) {
            this.notification.add("Respuesta recibida", { type: "success" });
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
            this.handleRecordingError(err);
        }
    }

    async stopRecording() {
        try {
            const blob = await this.audioRecorder.stopRecording();
            this.state.recording = false;
            if (blob && blob.size > 0) {
                await this.audioNoteManager.createAudioNote(blob);
            } else {
                this.state.error = "No se capturó audio";
            }
        } catch (err) {
            this.state.error = err.message;
        }
    }

    handleRecordingError(err) {
        this.state.error = err.message;
        this.state.recording = false;
    }

    get sortedNotes() {
        return this.audioNoteManager.sortedNotes;
    }

    async deleteNote(noteId) {
        await this.audioNoteManager.deleteNote(noteId);
    }

    // === ENVÍO A N8N CON REINICIO GARANTIZADO ===
    async sendToN8N() {
        const notesToSend = this.audioNoteManager.getNotesForSending();
        const contactsToSend = this.contactManager.getSelectedContacts();

        if (notesToSend.length === 0 && contactsToSend.length === 0) {
            this.notification.add("No hay datos para enviar", { type: "warning" });
            return;
        }

        // Activar estado de envío
        this.state.isSending = true;
        this.state.loading_response = true;
        this.state.final_message = '';
        this.state.answer_ia = '';

        // Configurar timeout de seguridad - 30 segundos
        this.safetyTimeout = setTimeout(() => {
            console.warn("⏰ TIMEOUT: Forzando reinicio del estado de envío");
            this.state.isSending = false;
            this.state.loading_response = false;
            this.notification.add("Proceso completado (timeout)", { type: "info" });
        }, 30000); // 30 segundos

        try {
            const success = await this.n8nService.sendToN8N(
                notesToSend,
                contactsToSend,
                null,
                null
            );

            // SIEMPRE reiniciar después de 2 segundos (incluso si fue exitoso)
            // Esto es por si el evento del bus nunca llega
            setTimeout(() => {
                if (this.state.isSending) {
                    console.log("🔄 Reinicio automático después del envío");
                    this.state.isSending = false;
                    this.state.loading_response = false;
                    
                    // Limpiar el timeout principal si aún existe
                    if (this.safetyTimeout) {
                        clearTimeout(this.safetyTimeout);
                        this.safetyTimeout = null;
                    }
                }
            }, 2000);

        } catch (error) {
            // Error inmediato - reiniciar estados y limpiar timeout
            if (this.safetyTimeout) {
                clearTimeout(this.safetyTimeout);
                this.safetyTimeout = null;
            }
            this.state.isSending = false;
            this.state.loading_response = false;
        }
    }
}