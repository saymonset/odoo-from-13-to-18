import { Component, useState, onWillStart, onWillUnmount } from "@odoo/owl";
import { useService, useBus } from "@web/core/utils/hooks";

export class VoiceRecorder extends Component {
    static template = "chatter_voice_note.VoiceRecorder";

    setup() {
        console.log('🔧 Iniciando VoiceRecorder - DIAGNÓSTICO BUS COMPLETO');
        
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.bus = useService("bus_service");
        
        this.user = this.env.user;
        this.userId = this.user?.id || 2;
        this.dbName = this.env.session?.db || 'dbcliente1_18';

        // ✅ INICIALIZACIÓN SEGURA DEL ESTADO
        this.state = useState({
            final_message: '',
            answer_ia: '',
            loading_response: false,
            debug_info: 'Inicializando diagnóstico BUS...',
            bus_events_received: 0,
            bus_diagnostic: this.getDefaultBusDiagnostic(),
            all_events: [],
            connection_state: 'unknown'
        });

        // ✅ DIAGNÓSTICO COMPLETO DEL BUS
        this.performBusDiagnostic();

        onWillUnmount(() => {
            this._cleanup();
        });
    }

    // ✅ MÉTODO PARA OBTENER DIAGNÓSTICO POR DEFECTO
    getDefaultBusDiagnostic() {
        return {
            bus_service: false,
            websocket: false,
            readyState: undefined,
            readyStateText: 'DESCONOCIDO',
            channels: [],
            url: null,
            lastEvent: null
        };
    }

    // ✅ MÉTODO SEGURO PARA OBTENER ESTADO DEL WEBSOCKET
    getSafeWebSocketState() {
        if (!this.state || !this.state.bus_diagnostic) {
            return 'DESCONOCIDO';
        }
        return this.state.bus_diagnostic.readyStateText || 'DESCONOCIDO';
    }

    // ✅ MÉTODO SEGURO PARA VERIFICAR CONEXIÓN
    getSafeConnectionClass() {
        if (!this.state || !this.state.bus_diagnostic) {
            return 'bg-secondary';
        }
        return this.state.bus_diagnostic.readyState === 1 ? 'bg-success' : 'bg-danger';
    }

    // ✅ MÉTODO SEGURO PARA VERIFICAR WEBSOCKET
    getSafeWebSocketStatus() {
        if (!this.state || !this.state.bus_diagnostic) {
            return false;
        }
        return this.state.bus_diagnostic.websocket || false;
    }

    async performBusDiagnostic() {
        console.log('🔍 Realizando diagnóstico completo del BUS...');
        
        // ✅ ACTUALIZAR ESTADO DE FORMA SEGURA
        this.state.bus_diagnostic = this.getDefaultBusDiagnostic();
        
        if (!this.bus) {
            console.error('❌ Bus service no disponible');
            this.state.debug_info = '❌ Bus service no disponible';
            return;
        }

        const allowedVersions = ['18.0', '18.0-7', '18.0.0', '18'];
        
        for (const version of allowedVersions) {
            console.log(`🔄 Probando versión: ${version}`);
            try {
                if (this.bus.websocket) {
                    this.bus.websocket.close();
                }
                
                await this.bus.start();
                
                if (this.bus.websocket?.readyState === 1) {
                    console.log(`✅ WebSocket conectado con versión: ${version}`);
                    break;
                }
            } catch (error) {
                console.log(`❌ Versión ${version} falló:`, error);
            }
            await new Promise(resolve => setTimeout(resolve, 1000));
        }

        // ✅ ACTUALIZACIÓN SEGURA DEL DIAGNÓSTICO
        const diagnostic = {
            bus_service: !!this.bus,
            websocket: !!this.bus.websocket,
            readyState: this.bus.websocket?.readyState,
            readyStateText: this.getWebSocketState(this.bus.websocket?.readyState),
            channels: this.bus.channels || [],
            url: this.bus.websocket?.url,
            lastEvent: null
        };

        this.state.bus_diagnostic = diagnostic;
        this.state.connection_state = diagnostic.readyStateText;
        
        console.log('📊 Diagnóstico BUS final:', diagnostic);
        
        if (diagnostic.readyState === 1) {
            this.setupDiagnosticListeners();
            this.state.debug_info = `✅ BUS CONECTADO - ${diagnostic.readyStateText}`;
        } else {
            this.state.debug_info = `❌ BUS NO CONECTADO - ${diagnostic.readyStateText}`;
        }
    }

    // ✅ MÉTODO QUE FALTABA: Configurar listeners
    setupDiagnosticListeners() {
        console.log('🎯 Configurando listeners de diagnóstico...');
        
        const userChannels = [
            `["${this.dbName}","res.partner",${this.userId}]`,
            `["${this.dbName}","audio_to_text.use.case",${this.userId}]`,
            '["broadcast"]'
        ];
        
        userChannels.forEach(channel => {
            try {
                useBus(
                    this.bus,
                    channel,
                    (ev) => {
                        console.log(`🎯 EVENTO CANAL ${channel}:`, ev);
                        this.handleDiagnosticEvent(ev, `canal_${channel}`);
                    }
                );
                console.log(`✅ Listener configurado para: ${channel}`);
            } catch (error) {
                console.error(`❌ Error listener ${channel}:`, error);
            }
        });

        const eventTypes = ["audio_to_text_response", "notification", "bus_diagnostic"];
        eventTypes.forEach(eventType => {
            try {
                useBus(
                    this.bus,
                    eventType,
                    (ev) => {
                        console.log(`🎯 EVENTO TIPO ${eventType}:`, ev);
                        this.handleDiagnosticEvent(ev, `tipo_${eventType}`);
                    }
                );
                console.log(`✅ Listener tipo evento: ${eventType}`);
            } catch (error) {
                console.error(`❌ Error listener ${eventType}:`, error);
            }
        });

        try {
            useBus(
                this.bus,
                "*",
                (ev) => {
                    console.log('🎯 CUALQUIER EVENTO BUS:', ev);
                    this.handleDiagnosticEvent(ev, 'cualquier_evento');
                }
            );
            console.log('✅ Listener todos los eventos configurado');
        } catch (error) {
            console.error('❌ Error listener todos los eventos:', error);
        }
    }

    // ✅ MÉTODO QUE FALTABA: Manejar eventos de diagnóstico
    handleDiagnosticEvent(ev, source) {
        try {
            console.log(`🔄 Evento desde ${source}:`, ev);
            
            this.state.bus_events_received++;
            
            const eventData = {
                source: source || 'desconocido',
                type: ev.type || 'sin_tipo',
                detail: ev.detail || ev,
                timestamp: new Date().toISOString()
            };
            
            if (!this.state.all_events) {
                this.state.all_events = [];
            }
            this.state.all_events.push(eventData);
            
            this.state.bus_diagnostic.lastEvent = {
                source: source,
                type: ev.type || 'sin_tipo',
                timestamp: new Date().toLocaleTimeString()
            };
            
            let message = ev.detail || ev;
            
            if (Array.isArray(message)) {
                message = message.find(item => 
                    item && (item.type === 'audio_to_text_response' || item.diagnostic)
                );
            }
            
            if (message && (message.type === 'audio_to_text_response' || message.diagnostic)) {
                console.log('✅ MENSAJE DIAGNÓSTICO RECIBIDO:', message);
                
                this.state.final_message = message.final_message || 'Mensaje diagnóstico recibido';
                this.state.answer_ia = message.answer_ia || 'Respuesta diagnóstico';
                this.state.loading_response = false;
                this.state.debug_info = `✅ BUS FUNCIONANDO! (${this.state.bus_events_received} eventos)`;
                
                this.notification.add("🎉 ¡BUS DIAGNÓSTICO EXITOSO!", {
                    type: "success",
                    sticky: true
                });
            } else {
                this.state.debug_info = `Evento ${source} recibido (${this.state.bus_events_received} total)`;
            }
            
        } catch (error) {
            console.error('❌ Error en handleDiagnosticEvent:', error);
            if (!this.state.all_events) {
                this.state.all_events = [];
            }
        }
    }

    getWebSocketState(readyState) {
        const states = {
            0: 'CONECTANDO',
            1: 'ABIERTO',
            2: 'CERRANDO', 
            3: 'CERRADO'
        };
        return states[readyState] || `DESCONOCIDO (${readyState})`;
    }

    _cleanup() {
        if (this._timeoutId) {
            clearTimeout(this._timeoutId);
        }
    }

    // ✅ MÉTODO QUE FALTABA: Mostrar estado actual (llamado desde template)
    showCurrentState() {
        const report = this.generateDiagnosticReport();
        console.log('🔍 Estado actual BUS:', report);
        
        this.notification.add(`🔍 BUS: ${this.state.connection_state} - ${this.state.bus_events_received} eventos`, {
            type: "info"
        });
        
        this.state.debug_info = `Estado: ${this.state.connection_state} - Eventos: ${this.state.bus_events_received}`;
    }

    // ✅ MÉTODO QUE FALTABA: Test de diagnóstico (llamado desde template)
    async testBusDiagnostic() {
        console.log('🧪 Test de diagnóstico BUS completo...');
        
        this.state.loading_response = true;
        this.state.final_message = '';
        this.state.answer_ia = '';
        this.state.debug_info = 'Iniciando diagnóstico BUS...';
        this.state.bus_events_received = 0;
        this.state.all_events = [];
        
        this._cleanup();
        
        this.performBusDiagnostic();
        
        this._timeoutId = setTimeout(() => {
            if (this.state.loading_response) {
                console.log('⏰ Diagnóstico BUS timeout');
                this.state.loading_response = false;
                this.state.debug_info = `DIAGNÓSTICO: ${this.state.bus_events_received} eventos recibidos`;
                
                const diagnosticReport = this.generateDiagnosticReport();
                console.log('📊 Reporte diagnóstico:', diagnosticReport);
                
                this.notification.add(`📊 Diagnóstico: ${this.state.bus_events_received} eventos`, {
                    type: "warning",
                    sticky: true
                });
            }
        }, 20000);
        
        await this.sendDiagnosticToBackend();
    }

    // ✅ MÉTODO QUE FALTABA: Enviar diagnóstico al backend
    async sendDiagnosticToBackend() {
        try {
            console.log('📞 Enviando solicitud de diagnóstico...');
            this.state.debug_info = 'Enviando diagnóstico al backend...';
            
            const result = await this.orm.call(
                'audio_to_text.use.case', 
                'test_bus_diagnostic', 
                []
            );
            
            console.log('✅ Backend diagnóstico respondió:', result);
            this.state.debug_info = `Diagnóstico backend: ${result.status} - Eventos: ${this.state.bus_events_received}`;
            
            this.notification.add("✅ Diagnóstico enviado al backend", {
                type: "info"
            });
            
        } catch (error) {
            console.error('❌ Error diagnóstico backend:', error);
            this.state.debug_info = 'Error en diagnóstico backend';
            this.state.loading_response = false;
        }
    }

    // ✅ MÉTODO QUE FALTABA: Generar reporte de diagnóstico
    generateDiagnosticReport() {
        return {
            bus_diagnostic: this.state.bus_diagnostic,
            events_received: this.state.bus_events_received,
            all_events: this.state.all_events,
            connection_state: this.state.connection_state,
            timestamp: new Date().toISOString()
        };
    }
}