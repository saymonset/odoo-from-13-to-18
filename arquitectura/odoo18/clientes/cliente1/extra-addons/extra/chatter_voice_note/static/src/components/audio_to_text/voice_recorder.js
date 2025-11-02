import { Component, useState, onWillStart, onWillUnmount } from "@odoo/owl";
import { useService, useBus } from "@web/core/utils/hooks";

export class VoiceRecorder extends Component {
    static template = "chatter_voice_note.VoiceRecorder";

    setup() {
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
        }
    }

    setupBusWithAutoFallback() {
        try {
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