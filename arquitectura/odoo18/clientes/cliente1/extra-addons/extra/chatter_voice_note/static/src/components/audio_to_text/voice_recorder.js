import { Component, useState, onWillStart, onWillUnmount } from "@odoo/owl";
import { useService, useBus } from "@web/core/utils/hooks";

export class VoiceRecorder extends Component {
    static template = "chatter_voice_note.VoiceRecorder";

    setup() {
<<<<<<< HEAD
        console.log('🔧 Iniciando VoiceRecorder - SISTEMA HÍBRIDO DEFINITIVO');
        
        this.orm = useService("orm");
        this.notification = useService("notification");
        
        // ✅ DIAGNÓSTICO AUTOMÁTICO DEL BUS
        this.bus = null;
        this.busAvailable = false;
        this.busDiagnostic = {
            available: false,
            websocket: false,
            readyState: 'unknown',
            channels: []
        };
        
        try {
            this.bus = useService("bus_service");
            this.busAvailable = true;
            this.busDiagnostic.available = true;
            
            // ✅ VERIFICAR WEBSOCKET
            if (this.bus.websocket) {
                this.busDiagnostic.websocket = true;
                this.busDiagnostic.readyState = this.bus.websocket.readyState;
                console.log('🔌 WebSocket del bus:', this.busDiagnostic);
            }
            
        } catch (error) {
            console.warn('🚫 Bus service no disponible');
        }

        this.user = this.env.user;
        this.userId = this.user?.id || 2;
        this.dbName = this.env.session?.db || 'dbcliente1_18';
=======
        // ✅ CORREGIDO: Obtener servicios de forma segura
        this.orm = useService("orm");
        this.notification = useService("notification");
        
        // ✅ CORREGIDO: Obtener bus_service de forma segura
        this.busService = this.getServiceSafely("bus_service");
        
        // ✅ CORREGIDO: Obtener user service de forma segura
        this.userService = this.getServiceSafely("user") || { userId: null };
        
        // ✅ CORREGIDO: Obtener audio_text_bus_service de forma segura
        this.audioTextBusService = this.getServiceSafely("audio_text_bus_service");

        this.currentStream = null;
>>>>>>> audio_to_text_bus

        this.state = useState({
            // Estados principales
            final_message: '',
            answer_ia: '',
            loading_response: false,
            isTesting: false,
            
            // ✅ SISTEMA DE MODO OPERATIVO
            operational_mode: 'polling', // 'bus' o 'polling'
            debug_info: 'Sistema híbrido iniciado',
            
            // Métricas
            polling_attempts: 0,
            bus_events_received: 0,
            total_tests: 0,
            bus_success_rate: 0,
            
            // Diagnóstico
            bus_available: this.busAvailable,
            bus_websocket_state: this.busDiagnostic.readyState,
            last_method_used: 'none'
        });

<<<<<<< HEAD
        // ✅ CONFIGURACIÓN INTELIGENTE
        this.setupIntelligentSystem();

        onWillUnmount(() => {
            this._cleanup();
        });
    }

    setupIntelligentSystem() {
        console.log('🎯 Configurando sistema inteligente...');
        
        // ✅ SI EL BUS ESTÁ DISPONIBLE, INTENTAR CONFIGURARLO
        if (this.busAvailable && this.busDiagnostic.websocket) {
            this.setupBusWithAutoFallback();
        } else {
            console.log('🔄 Modo polling - Bus no disponible');
            this.state.operational_mode = 'polling';
            this.state.debug_info = 'Modo: Polling (bus no detectado)';
=======
        onWillStart(async () => {
            this.state.loading_response = false;
            if (this.busService && this.busService.addChannel) {
                this.busService.addChannel("audio_to_text_channel_1");
            }
        });

        // ✅ CORREGIDO: Asegurar que el handler esté correctamente vinculado
        this.handleAudioResponse = this.handleAudioResponse.bind(this);
        useBus(this.env.bus, "AUDIO_TEXT_RESPONSE", this.handleAudioResponse);
        
        onWillUnmount(() => {
            if (this.busService && this.busService.leave) {
                this.busService.leave("audio_to_text_channel_1");
            }
        });
    }

    // ✅ NUEVO: Método para obtener servicios de forma segura
    getServiceSafely(serviceName) {
        try {
            return useService(serviceName);
        } catch (error) {
            console.warn(`Servicio ${serviceName} no disponible:`, error.message);
            return null;
        }
    }

    // ✅ NUEVO: Método separado para manejar respuestas de audio
    handleAudioResponse(ev) {
        const payload = ev.detail;
        console.log("Evento AUDIO_TEXT_RESPONSE recibido:", payload);
        
        if (payload.final_message) {
            this.state.final_message = payload.final_message;
        }
        if (payload.answer_ia) {
            this.state.answer_ia = payload.answer_ia;
        }
        
        this.state.loading_response = false;
        this.state.notes = [];
        this.state.selectedContacts = [];
        
        if (payload.final_message) {
            this.notification.add(
                "Respuesta de audio recibida y procesada", 
                { type: "success" }
            );
>>>>>>> audio_to_text_bus
        }
    }

    setupBusWithAutoFallback() {
        try {
<<<<<<< HEAD
            console.log('🔊 Intentando configurar useBus...');
            
            const userChannel = `["${this.dbName}","res.partner",${this.userId}]`;
            
            // ✅ CONFIGURAR useBus CON MANEJO DE ERRORES
            useBus(
                this.bus,
                userChannel,
                (ev) => {
                    console.log('🎯 useBus - Evento recibido!', ev);
                    this.handleBusSuccess(ev.detail, 'useBus_channel');
                }
            );
=======
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

    // === GRABACIÓN ===
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
            
            this.currentStream = stream;
            const recorder = new MediaRecorder(stream);
            const chunks = [];

            recorder.ondataavailable = (e) => {
                if (e.data.size > 0) {
                    chunks.push(e.data);
                }
            };
            
            recorder.onstop = async () => {
                stream.getTracks().forEach(track => track.stop());
                this.currentStream = null;
                
                const blob = new Blob(chunks, { type: "audio/webm" });
                const url = URL.createObjectURL(blob);
                const name = `voice_note_${new Date().toISOString()}.webm`;
                const tempId = `temp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
>>>>>>> audio_to_text_bus

            useBus(
                this.bus,
                "audio_to_text_response", 
                (ev) => {
                    console.log('🎯 useBus - Evento por tipo!', ev);
                    this.handleBusSuccess(ev.detail, 'useBus_event');
                }
            );

            console.log('✅ useBus configurado - Esperando eventos...');
            
        } catch (error) {
            console.error('❌ useBus falló - Cambiando a polling:', error);
            this.state.operational_mode = 'polling';
            this.state.debug_info = 'useBus falló - Modo polling';
        }
    }

    handleBusSuccess(eventData, source) {
        try {
            console.log(`✅ BUS FUNCIONANDO desde ${source}:`, eventData);
            
            this.state.bus_events_received++;
            this.state.operational_mode = 'bus';
            this.state.last_method_used = 'bus';
            
            let message = eventData;
            if (Array.isArray(eventData)) {
                message = eventData[0];
            }
            
            if (message && (message.type === 'new_response' || message.type === 'audio_to_text_response')) {
                // ✅ DETENER POLLING SI ESTÁ ACTIVO
                this.stopPolling();
                
                // ✅ ACTUALIZAR ESTADO
                this.state.final_message = message.final_message;
                this.state.answer_ia = message.answer_ia;
                this.state.loading_response = false;
                this.state.isTesting = false;
                this.state.debug_info = `✅ Bus activo (${this.state.bus_events_received} eventos)`;
                
                this.notification.add("🚀 ¡useBus FUNCIONANDO! Evento recibido", {
                    type: "success",
                    sticky: true
                });
                
                console.log('🎉 useBus: Comunicación en tiempo real funcionando');
            }
            
        } catch (error) {
            console.error('❌ Error procesando evento bus:', error);
        }
    }

<<<<<<< HEAD
    // ✅ MÉTODO PRINCIPAL MEJORADO
    async testCommunication() {
        console.log('🧪 Test comunicación mejorado...');
        
        this.state.total_tests++;
        this.state.isTesting = true;
        this.state.loading_response = true;
        this.state.final_message = '';
        this.state.answer_ia = '';
        this.state.debug_info = 'Iniciando test...';
        this.state.polling_attempts = 0;
        
        // ✅ CALCULAR TASA DE ÉXITO DEL BUS
        const busSuccessRate = this.state.bus_events_received / this.state.total_tests * 100;
        this.state.bus_success_rate = Math.round(busSuccessRate);
        
        this._cleanup();
        
        // ✅ ESTRATEGIA INTELIGENTE
        if (this.state.bus_success_rate > 50 && this.state.operational_mode === 'bus') {
            console.log('🎯 Confiando en bus (alta tasa de éxito)');
            this.state.debug_info = 'Estrategia: Priorizando bus';
            this.startBusMonitoring();
        } else {
            console.log('🔄 Usando polling (más confiable)');
            this.state.debug_info = 'Estrategia: Polling confiable';
            this.startPollingForResponse();
        }
        
        // ✅ TIMEOUT GLOBAL
        this._timeoutId = setTimeout(() => {
            if (this.state.loading_response) {
                console.log('⏰ Timeout global del test');
                this._cleanup();
=======
    // Método para subir audio
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
        this.state.final_message = '';
        this.state.answer_ia = '';

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
                user_id: this.userService.userId,
                bus_channel: "audio_to_text_channel_1"
            };

            const response = await fetch(N8N_WEBHOOK_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });

            if (response.ok) {
                this.notification.add(
                    `Enviado: ${notesToSend.length} audios, ${this.state.selectedContacts.length} contactos. Esperando respuesta...`,
                    { type: "info" }
                );
            } else {
                const errorText = await response.text();
                console.error("Error n8n:", response.status, errorText);
                this.notification.add(
                    `Error al enviar: ${response.status}`,
                    { type: "danger" }
                );
>>>>>>> audio_to_text_bus
                this.state.loading_response = false;
                this.state.isTesting = false;
                this.state.debug_info = `Timeout - Modo: ${this.state.operational_mode}`;
            }
        }, 10000);
        
        // ✅ ENVIAR AL BACKEND
        await this.sendToBackend();
    }

    startBusMonitoring() {
        console.log('🔍 Monitoreando bus...');
        // En este modo, confiamos en que useBus capturará el evento
        // Solo usamos timeout como respaldo
    }

    startPollingForResponse() {
        console.log('🔄 Iniciando polling confiable...');
        
        if (this._pollingInterval) {
            clearInterval(this._pollingInterval);
        }
        
        let attempts = 0;
        const maxAttempts = 5; // 10 segundos máximo
        
        this._pollingInterval = setInterval(async () => {
            if (!this.state.loading_response) {
                this.stopPolling();
                return;
            }
            
            attempts++;
            this.state.polling_attempts = attempts;
            this.state.debug_info = `Polling: ${attempts}/${maxAttempts} | Bus eventos: ${this.state.bus_events_received}`;
            
            console.log(`📡 Polling ${attempts}`);
            
            try {
                const result = await this.orm.call(
                    'audio_to_text.use.case', 
                    'check_for_response', 
                    [{ user_id: this.userId }]
                );
                
                if (result.status === 'response_available') {
                    console.log('✅ Respuesta via polling');
                    this.stopPolling();
                    
                    this.state.final_message = result.final_message;
                    this.state.answer_ia = result.answer_ia;
                    this.state.loading_response = false;
                    this.state.isTesting = false;
                    this.state.last_method_used = 'polling';
                    this.state.debug_info = '✅ Polling exitoso';
                    
                    this.notification.add("✅ Comunicación exitosa (Polling)", {
                        type: "success"
                    });
                } else if (attempts >= maxAttempts) {
                    console.log('⏰ Polling alcanzó máximo de intentos');
                    this.stopPolling();
                }
            } catch (error) {
                console.error('❌ Error en polling:', error);
                this.state.debug_info = `Error polling: ${error.message}`;
            }
        }, 2000);
    }

    stopPolling() {
        if (this._pollingInterval) {
            clearInterval(this._pollingInterval);
            this._pollingInterval = null;
        }
    }

    _cleanup() {
        this.stopPolling();
        if (this._timeoutId) {
            clearTimeout(this._timeoutId);
            this._timeoutId = null;
        }
    }

    async sendToBackend() {
        try {
            this.state.debug_info = 'Enviando solicitud...';
            const result = await this.orm.call('audio_to_text.use.case', 'test', []);
            
            console.log('✅ Backend respondió:', result);
            this.state.debug_info = `Backend OK | Modo: ${this.state.operational_mode}`;
            
        } catch (error) {
            console.error('❌ Error enviando al backend:', error);
            this.state.debug_info = 'Error backend';
            this.state.loading_response = false;
            this.state.isTesting = false;
        }
    }

    // ✅ MÉTODO PARA FORZAR MODO BUS (para pruebas)
    async testBusForced() {
        console.log('🧪 Test forzado de bus...');
        
        this.state.isTesting = true;
        this.state.loading_response = true;
        this.state.debug_info = 'Test forzado de bus...';
        this.state.operational_mode = 'bus';
        
        this._cleanup();
        
        // ✅ TIMEOUT CORTO PARA BUS
        this._timeoutId = setTimeout(() => {
            if (this.state.loading_response) {
                console.log('⏰ Bus timeout - Cambiando a polling');
                this.state.operational_mode = 'polling';
                this.state.debug_info = 'Bus timeout - Polling activado';
                this.startPollingForResponse();
            }
        }, 5000);
        
        await this.sendToBackend();
    }
}