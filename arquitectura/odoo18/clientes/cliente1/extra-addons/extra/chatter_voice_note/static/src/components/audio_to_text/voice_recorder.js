/** @odoo-module **/
import { Component, useState, onWillStart, onWillUnmount, useRef } from "@odoo/owl";
import { useService, useBus } from "@web/core/utils/hooks";
import { ContactManager } from "./contact_manager";
import { AudioRecorder } from "./audio_recorder";
import { AudioNoteManager } from "./audio_note_manager";
import { N8NService } from "./n8n_service";
import { BUS_CHANNELS } from "./constants";

export class VoiceRecorder extends Component {
    static template = "chatter_voice_note.VoiceRecorder";

    setup() {
        console.log("🔧 Setup VoiceRecorder - Modo DUAL (Bus + Polling)");
        this.initServices();
        this.initManagers();
        this.state = useState(this.getInitialState());
        
        // Referencia para forzar actualizaciones
        this.forceUpdateRef = useRef(0);
        
        // Variables para el sistema dual
        this.pollingInterval = null;
        this.pollingAttempts = 0;
        this.maxPollingAttempts = 30; // 30 intentos = 60 segundos
        this.lastRequestId = null;
        
        this.setupEventListeners();
        this.safetyTimeout = null;
        
        onWillStart(() => this.onComponentStart());
        onWillUnmount(() => this.onComponentUnmount());
    }

    initServices() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.busService = useService("bus_service");
        this.userService = { userId: null };
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
            error: null,
            responseMethod: 'none' // 'bus', 'polling', 'none'
        };
    }

    setupEventListeners() {
        console.log("🔧 Configurando sistema DUAL: Bus + Polling");
        
        // Handler para eventos del bus (Método preferido)
        const handleBusResponse = (ev) => {
            console.log("🎯 EVENTO BUS RECIBIDO:", ev.detail);
            
            const payload = ev.detail;
            this.processResponse(payload, 'bus');
        };

        // Escuchar el evento del bus
        useBus(this.env.bus, "new_response", handleBusResponse);
        
        console.log("🎧 Escuchando evento del bus: new_response");
    }

    // Procesar respuesta (común para bus y polling)
    processResponse(payload, method) {
        console.log(`✅ Respuesta recibida por ${method}:`, payload);
        
        // Limpiar timeouts e intervals
        this.cleanupTimers();
        
        // Actualizar estados
        this.state.isSending = false;
        this.state.loading_response = false;
        this.state.final_message = payload.final_message || '';
        this.state.answer_ia = payload.answer_ia || '';
        this.state.responseMethod = method;
        
        // Forzar actualización de la vista
        this.forceUpdateRef.value++;
        
        // Resetear managers
        this.audioNoteManager.reset();
        this.contactManager.reset();
        
        console.log("🔄 Estados actualizados:", {
            final_message: this.state.final_message,
            answer_ia: this.state.answer_ia,
            method: method
        });
        
        if (payload.final_message) {
            this.notification.add(`✅ Respuesta recibida (vía ${method})`, { type: "success" });
        }
    }

    // Iniciar polling como fallback
    startPolling(requestId) {
        console.log("🔄 Iniciando polling como fallback...");
        this.lastRequestId = requestId;
        this.pollingAttempts = 0;
        
        this.pollingInterval = setInterval(async () => {
            this.pollingAttempts++;
            console.log(`📡 Polling intento ${this.pollingAttempts}/${this.maxPollingAttempts}`);
            
            if (this.pollingAttempts >= this.maxPollingAttempts) {
                console.warn("⏰ Polling timeout - demasiados intentos");
                this.stopPolling();
                this.state.isSending = false;
                this.state.loading_response = false;
                this.notification.add("❌ No se pudo obtener respuesta", { type: "warning" });
                return;
            }
            
            await this.checkForResponse();
            
        }, 2000); // Polling cada 2 segundos
    }

    // Verificar respuestas (simulación - adaptar según tu backend)
    async checkForResponse() {
        try {
            console.log("🔍 Verificando respuesta del backend...");
            
            // SIMULACIÓN: Aquí deberías hacer una llamada real a tu backend
            // para verificar si hay respuesta para lastRequestId
            // Por ahora simulamos una respuesta después de 3 intentos
            
            if (this.pollingAttempts === 3) {
                console.log("🎯 Simulando respuesta del polling");
                const simulatedResponse = {
                    final_message: "Este es un mensaje final simulado via polling",
                    answer_ia: "Esta es una respuesta IA simulada via polling"
                };
                this.processResponse(simulatedResponse, 'polling');
            }
            
        } catch (error) {
            console.error("❌ Error en polling:", error);
        }
    }

    // Detener polling
    stopPolling() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
            console.log("🛑 Polling detenido");
        }
    }

    // Limpiar todos los timers
    cleanupTimers() {
        // Limpiar timeout de seguridad
        if (this.safetyTimeout) {
            clearTimeout(this.safetyTimeout);
            this.safetyTimeout = null;
        }
        
        // Limpiar polling
        this.stopPolling();
    }

    async onComponentStart() {
        this.state.loading_response = false;
        if (this.busService?.addChannel) {
            console.log("📡 Suscribiéndose al canal del bus:", BUS_CHANNELS.AUDIO_TEXT);
            this.busService.addChannel(BUS_CHANNELS.AUDIO_TEXT);
        }
    }

    onComponentUnmount() {
        console.log("🔧 Componente desmontado - limpiando recursos");
        if (this.state.recording) {
            this.audioRecorder.cleanup();
        }
        if (this.busService?.leave) {
            this.busService.leave(BUS_CHANNELS.AUDIO_TEXT);
        }
        
        // Limpiar todos los timers
        this.cleanupTimers();
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
            this.forceUpdateRef.value++;
        } catch (err) {
            this.state.error = err.message;
            this.state.recording = false;
            this.forceUpdateRef.value++;
        }
    }

    async stopRecording() {
        try {
            const blob = await this.audioRecorder.stopRecording();
            this.state.recording = false;
            this.forceUpdateRef.value++;
            
            if (blob && blob.size > 0) {
                await this.audioNoteManager.createAudioNote(blob);
            } else {
                this.state.error = "No se capturó audio";
                this.forceUpdateRef.value++;
            }
        } catch (err) {
            this.state.error = err.message;
            this.forceUpdateRef.value++;
        }
    }

    get sortedNotes() {
        return this.audioNoteManager.sortedNotes;
    }

    async deleteNote(noteId) {
        await this.audioNoteManager.deleteNote(noteId);
    }

    async sendToN8N() {
        const notesToSend = this.audioNoteManager.getNotesForSending();
        const contactsToSend = this.contactManager.getSelectedContacts();

        if (notesToSend.length === 0 && contactsToSend.length === 0) {
            this.notification.add("No hay datos para enviar", { type: "warning" });
            return;
        }

        // Generar ID único para esta solicitud
        const requestId = `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        
        // Activar estado de envío
        this.state.isSending = true;
        this.state.loading_response = true;
        this.state.final_message = '';
        this.state.answer_ia = '';
        this.state.responseMethod = 'none';
        this.forceUpdateRef.value++;

        console.log("📤 Enviando a N8N...", { requestId });

        // Timeout de seguridad principal - 60 segundos
        this.safetyTimeout = setTimeout(() => {
            console.warn("⏰ TIMEOUT PRINCIPAL: Forzando reinicio");
            this.cleanupTimers();
            this.state.isSending = false;
            this.state.loading_response = false;
            this.forceUpdateRef.value++;
            this.notification.add("⏰ Tiempo de espera agotado", { type: "warning" });
        }, 60000);

        try {
            // Enviar a N8N (incluyendo el requestId en el payload si es posible)
            await this.n8nService.sendToN8N(
                notesToSend,
                contactsToSend,
                null,
                null,
                requestId // Pasar el requestId si tu N8N service lo soporta
            );

            console.log("✅ Envío a N8N completado - Iniciando sistema dual");
            
            // Iniciar polling como fallback después de 5 segundos
            setTimeout(() => {
                if (this.state.isSending) {
                    console.log("🔄 Bus no respondió en 5s - Activando polling");
                    this.startPolling(requestId);
                }
            }, 5000);

            // Reinicio automático después de 10 segundos (último recurso)
            setTimeout(() => {
                if (this.state.isSending) {
                    console.log("🔄 Reinicio automático de seguridad");
                    this.cleanupTimers();
                    this.state.isSending = false;
                    this.state.loading_response = false;
                    this.forceUpdateRef.value++;
                }
            }, 10000);

        } catch (error) {
            console.error("❌ Error en envío:", error);
            this.cleanupTimers();
            this.state.isSending = false;
            this.state.loading_response = false;
            this.forceUpdateRef.value++;
        }
    }
}