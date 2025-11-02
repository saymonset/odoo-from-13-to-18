import { Component, useState, onWillStart, onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class VoiceRecorder extends Component {
    static template = "chatter_voice_note.VoiceRecorder";

    setup() {
        console.log('🔧 Iniciando setup de VoiceRecorder con POLLING...');
        
        this.orm = useService("orm");
        this.notification = useService("notification");
        
        this.user = this.env.user;
        this.userId = this.user?.id || 2;

        this.state = useState({
            recording: false,
            uploading: false,
            notes: [],
            error: null,
            isSending: false,
            searchTerm: '',
            availableContacts: [],
            selectedContacts: [],
            final_message: '',
            answer_ia: '',
            loading_response: false,
            isTesting: false,
            debug_info: 'Modo POLLING activado',
            // ✅ NUEVO: estado para polling
            polling_attempts: 0
        });

        onWillUnmount(() => {
            this._cleanup();
        });
    }

    _cleanup() {
        if (this._pollingInterval) {
            clearInterval(this._pollingInterval);
        }
        if (this._timeoutId) {
            clearTimeout(this._timeoutId);
        }
    }

async startPollingForResponse() {
    console.log('🔄 Iniciando polling para respuesta...');
    
    if (this._pollingInterval) {
        clearInterval(this._pollingInterval);
    }
    
    let attempts = 0;
    const maxAttempts = 10;
    
    this._pollingInterval = setInterval(async () => {
        attempts++;
        this.state.polling_attempts = attempts;
        this.state.debug_info = `Polling... Intento ${attempts}/${maxAttempts}`;
        
        console.log(`📡 Polling intento ${attempts}`);
        
        try {
            // ✅ LLAMADA SIMPLIFICADA - SOLO PARA PRUEBAS
            const result = await this.orm.call(
                'audio_to_text.use.case', 
                'check_for_response', 
                [{
                    user_id: this.userId
                }]
            );
            
            if (result.status === 'response_available') {
                console.log('✅ Respuesta encontrada via polling:', result);
                clearInterval(this._pollingInterval);
                
                this.state.final_message = result.final_message;
                this.state.answer_ia = result.answer_ia;
                this.state.loading_response = false;
                this.state.isTesting = false;
                this.state.debug_info = 'Respuesta recibida via POLLING ✅';
                
                this.notification.add("✅ Respuesta recibida (via Polling)", {
                    type: "success",
                    sticky: true
                });
            } else if (attempts >= maxAttempts) {
                console.log('⏰ Polling timeout');
                clearInterval(this._pollingInterval);
                this.state.loading_response = false;
                this.state.isTesting = false;
                this.state.debug_info = 'Timeout polling - Sin respuesta';
                
                this.notification.add("⚠️ No se recibió respuesta (timeout polling)", {
                    type: "warning"
                });
            }
            
        } catch (error) {
            console.error('❌ Error en polling:', error);
            this.state.debug_info = `Error polling: ${error.message}`;
            
            // En caso de error, detener polling después de 3 intentos fallidos
            if (attempts >= 3) {
                clearInterval(this._pollingInterval);
                this.state.loading_response = false;
                this.state.isTesting = false;
                this.state.debug_info = 'Error persistente en polling';
            }
        }
    }, 2000); // 2 segundos
}
    async testManualBus() {
        console.log('🧪 Test con POLLING...');
        
        try {
            this.state.isTesting = true;
            this.state.loading_response = true;
            this.state.final_message = '';
            this.state.answer_ia = '';
            this.state.debug_info = 'Iniciando test con polling...';
            this.state.polling_attempts = 0;
            
            // ✅ LIMPIAR INTERVALOS ANTERIORES
            this._cleanup();
            
            // ✅ TIMEOUT DE SEGURIDAD
            this._timeoutId = setTimeout(() => {
                if (this.state.loading_response) {
                    console.log('⏰ Timeout global - Deteniendo polling');
                    this._cleanup();
                    this.state.loading_response = false;
                    this.state.isTesting = false;
                    this.state.debug_info = 'Timeout global';
                    
                    this.notification.add("⚠️ Timeout global - Verificar servidor", {
                        type: "warning"
                    });
                }
            }, 35000); // 35 segundos
            
            // ✅ INICIAR POLLING INMEDIATAMENTE
            this.startPollingForResponse();
            
            // ✅ LLAMAR AL BACKEND PARA GENERAR RESPUESTA
            await this.testBus();
            
        } catch (error) {
            console.error('❌ Error en testManualBus:', error);
            this._cleanup();
            this.state.loading_response = false;
            this.state.isTesting = false;
            this.state.debug_info = 'Error en test';
            
            this.notification.add("❌ Error: " + error.message, {
                type: "danger"
            });
        }
    }

    async testBus() {
        console.log('🔄 Llamando al backend...');
        
        try {
            this.state.debug_info = 'Enviando solicitud al backend...';
            const result = await this.orm.call('audio_to_text.use.case', 'test', []);
            
            console.log('✅ Backend respondió:', result);
            this.state.debug_info = `Backend: ${result.status} - Polling activo`;
            
            this.notification.add("✅ Solicitud enviada al backend - Esperando respuesta...", {
                type: "info"
            });
            
        } catch (error) {
            console.error('❌ Error en testBus:', error);
            this._cleanup();
            this.state.loading_response = false;
            this.state.isTesting = false;
            this.state.debug_info = 'Error llamando al backend';
            
            this.notification.add("❌ Error backend: " + error.message, {
                type: "danger"
            });
        }
    }

    // ... (el resto de los métodos se mantienen igual)
}