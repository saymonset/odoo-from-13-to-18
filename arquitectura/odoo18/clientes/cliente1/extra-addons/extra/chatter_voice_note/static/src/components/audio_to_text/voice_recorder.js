import { Component, useState, onWillStart, onWillUnmount } from "@odoo/owl";
import { useService, useBus } from "@web/core/utils/hooks";

export class VoiceRecorder extends Component {
    static template = "chatter_voice_note.VoiceRecorder";

    setup() {
        console.log('🔧 Iniciando setup de VoiceRecorder...');
        
        // ✅ SERVICIOS CON PROTECCIÓN
        try {
            this.orm = useService("orm");
            this.notification = useService("notification");
            
            // ✅ BUS SERVICE CON FALLBACK
            try {
                this.bus = useService("bus_service");
            } catch (busError) {
                console.warn('⚠️ Bus service no disponible:', busError);
                this.bus = null;
            }
        } catch (error) {
            console.error('❌ Error crítico cargando servicios:', error);
            // Fallback mínimo para evitar crash
            this.state = useState({ error: 'Error inicializando componente' });
            return;
        }

        this.user = this.env.user;
        this.userId = this.user?.id || 2;
        
        console.log('👤 Usuario ID:', this.userId);

        this.currentStream = null;

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
            // ✅ NUEVO: estado para debug seguro
            debug_info: 'Componente inicializado'
        });

        // ✅ LISTENERS SOLO SI BUS ESTÁ DISPONIBLE
        if (this.bus) {
            this._setupBusListeners();
        } else {
            console.warn('🚫 Bus no disponible - listeners desactivados');
            this.state.debug_info = 'Bus service no disponible';
        }

        onWillStart(() => {
            console.log('🚀 onWillStart ejecutado');
            this.state.loading_response = false;
        });

        onWillUnmount(() => {
            this._cleanup();
        });
    }

    _cleanup() {
        // ✅ LIMPIEZA SEGURA
        try {
            if (this.state.recording && this.state.mediaRecorder) {
                this.state.mediaRecorder.stop();
            }
            if (this.currentStream) {
                this.currentStream.getTracks().forEach(track => track.stop());
            }
            if (this._timeoutId) {
                clearTimeout(this._timeoutId);
            }
        } catch (error) {
            console.warn('⚠️ Error en cleanup:', error);
        }
    }

    _setupBusListeners() {
    console.log('🔊 Configurando listeners del bus...');
    
    try {
        // ✅ SUSCRIPCIÓN EXPLÍCITA AL CANAL DEL USUARIO
        const userChannel = `["${this.env.session.db}","res.partner",${this.userId}]`;
        console.log('🎯 Suscribiendo al canal:', userChannel);
        
        // ✅ SUSCRIBIRSE AL CANAL ESPECÍFICO
        this.bus.addChannel(userChannel);
        
        // ✅ LISTENER PARA EL CANAL ESPECÍFICO
        useBus(
            this.bus, 
            userChannel,  // ✅ ESCUCHAR EN EL CANAL ESPECÍFICO, NO EN EL EVENTO GENERAL
            (ev) => {
                console.log('🎯 EVENTO RECIBIDO EN CANAL ESPECÍFICO:', {
                    canal: userChannel,
                    evento: ev
                });
                
                if (this.state.isTesting) {
                    console.log('🧪 EVENTO RECIBIDO DURANTE TEST');
                    this.state.isTesting = false;
                }
                
                this._handleAudioResponse(ev);
            }
        );
        
        // ✅ LISTENER ALTERNATIVO PARA EL TIPO DE EVENTO (como backup)
        useBus(
            this.bus, 
            "audio_to_text_response", 
            (ev) => {
                console.log('🎯 EVENTO RECIBIDO POR TIPO:', ev);
                
                if (this.state.isTesting) {
                    console.log('🧪 EVENTO RECIBIDO DURANTE TEST (por tipo)');
                    this.state.isTesting = false;
                }
                
                this._handleAudioResponse(ev);
            }
        );
        
        console.log('✅ Listeners del bus configurados correctamente');
        this.state.debug_info = `Listeners activos - Canal: ${userChannel}`;
        
    } catch (error) {
        console.error('❌ Error configurando listeners:', error);
        this.state.debug_info = 'Error en listeners';
    }
}

   async testManualBus() {
    console.log('🧪 Test manual del bus...');
    
    try {
        // ✅ RESET COMPLETO
        this.state.isTesting = true;
        this.state.loading_response = true;
        this.state.final_message = '';
        this.state.answer_ia = '';
        this.state.debug_info = 'Iniciando test manual...';
        
        console.log('🔄 Estado resetado para test');
        
        // ✅ LIMPIAR TIMEOUT ANTERIOR
        if (this._timeoutId) {
            clearTimeout(this._timeoutId);
        }
        
        // ✅ TIMEOUT DE SEGURIDAD (aumentado a 15 segundos)
        this._timeoutId = setTimeout(() => {
            if (this.state.loading_response) {
                console.log('⏰ Timeout - No llegó notificación después de 15s');
                this.state.loading_response = false;
                this.state.isTesting = false;
                this.state.debug_info = 'Timeout - Verificar configuración del bus';
                
                this.notification.add("⚠️ Timeout - No se recibió notificación en 15 segundos", { 
                    type: "warning",
                    sticky: true 
                });
            }
        }, 15000); // 15 segundos
        
        // ✅ ESPERAR UN MOMENTO PARA QUE LOS LISTENERS ESTÉN LISTOS
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // ✅ LLAMADA AL BACKEND
        await this.testBus();
        
    } catch (error) {
        console.error('❌ Error en testManualBus:', error);
        this.state.loading_response = false;
        this.state.isTesting = false;
        this.state.debug_info = 'Error en test manual';
        
        this.notification.add("❌ Error en test manual: " + error.message, { 
            type: "danger" 
        });
    }
}
    async testBus() {
        console.log('🔄 Iniciando testBus...');
        
        try {
            this.state.debug_info = 'Llamando al backend...';
            const result = await this.orm.call('audio_to_text.use.case', 'test', []);
            
            console.log('✅ Backend respondió:', result);
            this.state.debug_info = `Backend: ${result.status}`;
            
            this.notification.add("✅ Prueba enviada al backend", { 
                type: "success"
            });
            
        } catch (error) {
            console.error('❌ Error en testBus:', error);
            this.state.loading_response = false;
            this.state.isTesting = false;
            this.state.debug_info = 'Error llamando al backend';
            
            this.notification.add("❌ Error: " + error.message, { 
                type: "danger" 
            });
        }
    }

   _handleAudioResponse(ev) {
    try {
        console.log('🎯 _handleAudioResponse ejecutado - Evento completo:', ev);
        
        // ✅ EXTRAER MENSAJE DE DIFERENTES FORMATOS
        let message = ev.detail;
        
        // Si el evento viene en formato de notificación Odoo
        if (ev.detail && Array.isArray(ev.detail)) {
            message = ev.detail[0];
        }
        
        console.log('📨 Mensaje procesado:', message);
        
        if (message && message.type === 'new_response') {
            console.log('✅ Mensaje new_response detectado - Actualizando estado...');
            
            // ✅ ACTUALIZACIÓN SEGURA DEL ESTADO
            this.state.final_message = message.final_message || 'Mensaje recibido sin contenido';
            this.state.answer_ia = message.answer_ia || 'Respuesta IA sin contenido';
            this.state.loading_response = false;
            this.state.debug_info = 'Notificación recibida ✅';
            
            console.log('🔄 Estado actualizado:', {
                final_message: this.state.final_message,
                answer_ia: this.state.answer_ia
            });
            
            // ✅ LIMPIAR TIMEOUT SI EXISTE
            if (this._timeoutId) {
                clearTimeout(this._timeoutId);
                this._timeoutId = null;
            }
            
            this.notification.add("✅ Notificación BUS recibida correctamente", { 
                type: "success",
                sticky: true
            });
            
        } else {
            console.log('⚠️ Mensaje con formato no esperado:', message);
            this.state.debug_info = `Formato no reconocido: ${message ? message.type : 'sin tipo'}`;
        }
        
    } catch (error) {
        console.error('❌ Error en _handleAudioResponse:', error);
        this.state.debug_info = 'Error procesando notificación';
        this.state.loading_response = false;
    }
}

    // === MÉTODOS DE CONTACTOS (SE MANTIENEN IGUAL) ===
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
        this.state.loading_response = true;

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