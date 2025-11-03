import { Component, useState, onWillUnmount } from "@odoo/owl";
import { useService, useBus } from "@web/core/utils/hooks";

export class VoiceRecorder extends Component {
    static template = "chatter_voice_note.VoiceRecorder";

    setup() {
        console.log('🔧 Iniciando VoiceRecorder - CONFIGURACIÓN SIMPLIFICADA');
        
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.bus = useService("bus_service");
        
        this.state = useState({
            final_message: '',
            answer_ia: '',
            loading_response: false,
            debug_info: 'Inicializando...',
            bus_events_received: 0,
            connection_state: 'unknown',
            all_events: []
        });

        // ✅ ESPERAR A QUE LA PÁGINA CARGUE COMPLETAMENTE
        setTimeout(() => {
            this.simpleBusTest();
        }, 3000);

        onWillUnmount(() => {
            this._cleanup();
        });
    }

    async simpleBusTest() {
        console.log('🧪 Test simple del BUS...');
        
        if (!this.bus) {
            this.state.debug_info = '❌ Bus service no disponible';
            return;
        }

        try {
            // ✅ INICIALIZACIÓN SIMPLE
            await this.bus.start();
            
            // ✅ VERIFICACIÓN BÁSICA
            const hasWebSocket = !!this.bus.websocket;
            const isConnected = this.bus.websocket?.readyState === 1;
            
            this.state.connection_state = isConnected ? 'CONECTADO' : 'DESCONECTADO';
            this.state.debug_info = `Bus: ${hasWebSocket ? 'Presente' : 'Ausente'}, WebSocket: ${isConnected ? 'Conectado' : 'Desconectado'}`;
            
            if (isConnected) {
                this.setupBasicListeners();
                this.state.debug_info = '✅ BUS CONECTADO - Listo para pruebas';
            } else {
                this.state.debug_info = '❌ BUS NO CONECTADO - Verificar servidor';
            }
            
        } catch (error) {
            console.error('❌ Error en simpleBusTest:', error);
            this.state.debug_info = `❌ Error: ${error.message}`;
        }
    }

    setupBasicListeners() {
        console.log('🎯 Configurando listeners básicos...');
        
        // Solo el canal de broadcast para pruebas
        try {
            useBus(
                this.bus,
                '["broadcast"]',
                (ev) => {
                    console.log('📨 Evento broadcast recibido:', ev);
                    this.handleBusEvent(ev, 'broadcast');
                }
            );
            console.log('✅ Listener broadcast configurado');
        } catch (error) {
            console.error('❌ Error listener broadcast:', error);
        }
    }

    handleBusEvent(ev, source) {
        this.state.bus_events_received++;
        
        const eventData = {
            source: source,
            type: ev.type || 'sin_tipo',
            timestamp: new Date().toLocaleTimeString(),
            data: ev.detail || ev
        };
        
        this.state.all_events.push(eventData);
        this.state.debug_info = `Eventos recibidos: ${this.state.bus_events_received}`;
        
        // Procesar mensajes de diagnóstico
        if (ev.detail && ev.detail.type === 'audio_to_text_response') {
            this.state.final_message = ev.detail.final_message || 'Mensaje recibido';
            this.state.answer_ia = ev.detail.answer_ia || 'Respuesta recibida';
            this.state.loading_response = false;
        }
    }

    async testBusDiagnostic() {
        console.log('🧪 Ejecutando diagnóstico...');
        
        this.state.loading_response = true;
        this.state.debug_info = 'Enviando prueba al servidor...';
        
        try {
            const result = await this.orm.call(
                'audio_to_text.use.case', 
                'test_bus_diagnostic', 
                []
            );
            
            console.log('✅ Servidor respondió:', result);
            this.state.debug_info = `Prueba enviada - ${result.status}`;
            
            // Timeout por si no llegan eventos
            setTimeout(() => {
                if (this.state.loading_response) {
                    this.state.loading_response = false;
                    this.state.debug_info = `Prueba completada - ${this.state.bus_events_received} eventos recibidos`;
                }
            }, 10000);
            
        } catch (error) {
            console.error('❌ Error en testBusDiagnostic:', error);
            this.state.loading_response = false;
            this.state.debug_info = 'Error en prueba';
        }
    }

    _cleanup() {
        if (this._timeoutId) {
            clearTimeout(this._timeoutId);
        }
    }

    // Métodos para el template
    getSafeConnectionClass() {
        return this.state.connection_state === 'CONECTADO' ? 'bg-success' : 'bg-danger';
    }

    getSafeWebSocketState() {
        return this.state.connection_state;
    }

    getSafeWebSocketStatus() {
        return this.state.connection_state === 'CONECTADO';
    }

    showCurrentState() {
        console.log('🔍 Estado actual:', this.state);
        this.notification.add(`Estado: ${this.state.connection_state} - Eventos: ${this.state.bus_events_received}`, {
            type: "info"
        });
    }
}