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
        console.log("🔧 Setup VoiceRecorder - COMUNICACIÓN CON BUS CORREGIDA");
        
        this.initServices();
        this.initManagers();
        
        this.state = useState({
            recording: false,
            isSending: false,
            final_message: '',
            answer_ia: '',
            loading_response: false,
            error: null,
            responseMethod: 'none',
            _updateCount: 0
        });
        
        this.pollingInterval = null;
        this.safetyTimeout = null;
        this.currentRequestId = null;
        this.busNotificationCallback = null;
        
        this.setupEventListeners();
        
        onWillStart(() => this.onComponentStart());
        onWillUnmount(() => this.onComponentUnmount());
    }

    initServices() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.busService = useService("bus_service");
        
        this.userService = { 
            userId: null,
            getUserId: async () => {
                try {
                    const user_id = await this.orm.call("res.users", "get_user_id", []);
                    return user_id;
                } catch (error) {
                    console.warn("No se pudo obtener user_id:", error);
                    return null;
                }
            }
        };
    }

    initManagers() {
        this.contactManager = new ContactManager(this.orm);
        this.audioRecorder = new AudioRecorder();
        this.audioNoteManager = new AudioNoteManager(this.orm, this.notification);
        this.n8nService = new N8NService(this.orm, this.notification);
    }

    forceRender() {
        this.state._updateCount++;
        console.log("🔄 Forzando re-render, count:", this.state._updateCount);
    }

    setupEventListeners() {
        console.log("🔧 Configurando listeners del bus");

        if (this.busService) {
            // ✅ SOLUCIÓN: Usar useBus con el bus service (forma correcta)
            useBus(this.busService, "notification", (ev) => {
                const notifications = ev.detail;
                console.log("📨 Notificaciones del bus recibidas:", notifications);
                
                notifications.forEach(notification => {
                    const [channel, message] = notification;
                    
                    if (channel === BUS_CHANNELS.AUDIO_TEXT && message.type === 'new_response') {
                        console.log("🎯 MENSAJE REAL DEL BACKEND:", message);
                        
                        // ✅ ACEPTAR RESPUESTAS CON O SIN request_id
                        const shouldProcess = !this.currentRequestId || 
                                            message.payload.request_id === this.currentRequestId;
                        
                        if (shouldProcess) {
                            console.log("✅ PROCESANDO RESPUESTA VÁLIDA");
                            this.processResponse(message.payload, 'bus_real');
                        } else {
                            console.log("⚠️ Respuesta para otra solicitud:", {
                                current: this.currentRequestId,
                                received: message.payload.request_id
                            });
                        }
                    }
                });
            });

            // Suscribirse al canal
            this.busService.addChannel(BUS_CHANNELS.AUDIO_TEXT);
            
            console.log("✅ Suscrito correctamente al canal:", BUS_CHANNELS.AUDIO_TEXT);
        } else {
            console.warn("⚠️ bus_service no disponible - usando solo polling");
        }
    }

    processResponse(payload, method) {
        console.log(`✅ Respuesta recibida por ${method}:`, payload);
        
        this.cleanupTimers();
        this.currentRequestId = null;
        
        this.state.isSending = false;
        this.state.loading_response = false;
        this.state.final_message = payload.final_message || 'No message received';
        this.state.answer_ia = payload.answer_ia || 'No AI response';
        this.state.responseMethod = method;
        
        this.forceRender();
        
        if (payload.final_message && payload.answer_ia) {
            setTimeout(() => {
                this.audioNoteManager.reset();
                this.contactManager.reset();
                this.forceRender();
            }, 2000);
        }
        
        console.log("🔄 Estados actualizados con datos del backend");
        
        if (payload.final_message) {
            this.notification.add(`✅ Respuesta recibida: ${payload.final_message}`, { 
                type: "success" 
            });
        }
    }

    startPolling(requestId) {
        console.log("🔄 Iniciando polling de respaldo...");
        let pollingCount = 0;
        const maxPollingAttempts = 3;
        
        this.pollingInterval = setInterval(() => {
            pollingCount++;
            console.log(`📡 Polling (${pollingCount}/${maxPollingAttempts}) para: ${requestId}`);
            
            if (pollingCount >= maxPollingAttempts) {
                console.log("🛑 Polling agotado - esperando solo bus");
                this.stopPolling();
                this.notification.add("⏳ Procesamiento en segundo plano...", { 
                    type: "info" 
                });
                return;
            }
        }, 3000);
    }

    stopPolling() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
        }
    }

    cleanupTimers() {
        if (this.safetyTimeout) {
            clearTimeout(this.safetyTimeout);
            this.safetyTimeout = null;
        }
        this.stopPolling();
    }

    async onComponentStart() {
        this.state.loading_response = false;
        console.log("🚀 Componente iniciado - Listo para recibir mensajes del bus");
    }

    onComponentUnmount() {
        if (this.state.recording) {
            this.audioRecorder.cleanup();
        }
        this.cleanupTimers();
        this.currentRequestId = null;
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
            this.forceRender();
        } catch (err) {
            this.state.error = err.message;
            this.state.recording = false;
            this.forceRender();
        }
    }

    async stopRecording() {
        try {
            const blob = await this.audioRecorder.stopRecording();
            this.state.recording = false;
            this.forceRender();
            
            if (blob && blob.size > 0) {
                await this.audioNoteManager.createAudioNote(blob);
                this.forceRender();
            } else {
                this.state.error = "No se capturó audio";
                this.forceRender();
            }
        } catch (err) {
            this.state.error = err.message;
            this.forceRender();
        }
    }

    get sortedNotes() {
        return this.audioNoteManager.sortedNotes;
    }

    async deleteNote(noteId) {
        await this.audioNoteManager.deleteNote(noteId);
        this.forceRender();
    }

    async sendToN8N() {
        const notesToSend = this.audioNoteManager.getNotesForSending();
        const contactsToSend = this.contactManager.getSelectedContacts();

        if (notesToSend.length === 0 && contactsToSend.length === 0) {
            this.notification.add("No hay datos para enviar", { type: "warning" });
            return;
        }

        this.currentRequestId = `req_${Date.now()}`;
        
        this.state.isSending = true;
        this.state.loading_response = true;
        this.state.final_message = '';
        this.state.answer_ia = '';
        this.state.responseMethod = 'none';
        this.forceRender();

        console.log("📤 Enviando a backend...", {
            requestId: this.currentRequestId,
            notes: notesToSend.length,
            contacts: contactsToSend.length
        });

        this.safetyTimeout = setTimeout(() => {
            console.warn("⏰ TIMEOUT: Procesamiento tomando más tiempo del esperado");
            this.cleanupTimers();
            this.state.isSending = false;
            this.state.loading_response = false;
            this.forceRender();
            this.notification.add("⏳ El procesamiento continúa en segundo plano...", { 
                type: "info" 
            });
        }, 20000);

        try {
            const immediateResponse = await this.n8nService.sendToN8N(
                notesToSend, 
                contactsToSend, 
                null, 
                null, 
                this.currentRequestId
            );

            console.log("✅ Respuesta inmediata del backend:", immediateResponse);
            
            if (immediateResponse.final_message && immediateResponse.answer_ia) {
                console.log("🎯 Procesando respuesta inmediata");
                this.processResponse(immediateResponse, 'immediate');
            } else {
                console.log("🔄 Esperando respuesta por bus...");
                this.startPolling(this.currentRequestId);
            }

        } catch (error) {
            console.error("❌ Error en envío:", error);
            this.cleanupTimers();
            this.currentRequestId = null;
            this.state.isSending = false;
            this.state.loading_response = false;
            this.forceRender();
        }
    }
}