import { Component, useState, onWillStart, onWillUnmount } from "@odoo/owl";
import { useService, useBus } from "@web/core/utils/hooks";

export class VoiceRecorder extends Component {
    static template = "chatter_voice_note.VoiceRecorder";

    setup() {
        console.log('🔧 Iniciando setup de VoiceRecorder...');
        
        // SERVICIOS ESTÁNDAR
        this.orm = useService("orm");
        this.bus = useService("bus_service");
        this.notification = useService("notification");

        this.user = this.env.user;
        this.userId = this.user?.id || 1;
        
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
            // ✅ AGREGAR ESTADO PARA CONTROLAR EL TEST MANUAL
            isTesting: false,
        });

        // ✅ LISTENERS DEL BUS - CORREGIDOS
        this._setupBusListeners();

        onWillStart(() => {
            console.log('🚀 onWillStart ejecutado');
            this.state.loading_response = false;
        });

        onWillUnmount(() => {
            if (this.state.recording && this.state.mediaRecorder) {
                this.state.mediaRecorder.stop();
            }
            if (this.currentStream) {
                this.currentStream.getTracks().forEach(track => track.stop());
            }
        });
    }

    _setupBusListeners() {
        console.log('🔊 Configurando listeners del bus...');
        
        // ✅ LISTENER PRINCIPAL
        useBus(
            this.bus, 
            "audio_to_text_response", 
            (ev) => {
                console.log('🎯 EVENTO audio_to_text_response RECIBIDO:', {
                    eventoCompleto: ev,
                    detail: ev.detail,
                    type: ev.type,
                    timestamp: new Date().toISOString()
                });
                
                // ✅ SI ESTAMOS EN MODO TEST, MANEJAR DE FORMA ESPECIAL
                if (this.state.isTesting) {
                    console.log('🧪 EVENTO RECIBIDO DURANTE TEST:', ev);
                    this.state.isTesting = false; // Desactivar modo test
                }
                
                this._handleAudioResponse(ev);
            }
        );
        
        console.log('✅ Listeners del bus configurados correctamente');
    }

    // ✅ MÉTODO SIMPLIFICADO - SIN USAR HOOKS
    async testManualBus() {
        console.log('🧪 Test manual del bus...');
        
        // ✅ ACTIVAR MODO TEST EN EL ESTADO
        this.state.isTesting = true;
        this.state.loading_response = true;
        
        console.log('🔍 Estado actualizado para test - isTesting:', this.state.isTesting);
        
        // Llamar al test después de 1 segundo para asegurar que los listeners están listos
        setTimeout(() => {
            this.testBus();
        }, 1000);
    }

    async testBus() {
        console.log('🔄 Iniciando testBus...');
        this.state.loading_response = true;
        this.state.final_message = '';
        this.state.answer_ia = '';
        
        try {
            console.log('📞 Llamando al método test del backend...');
            const result = await this.orm.call('audio_to_text.use.case', 'test', []);
            console.log('✅ Test ejecutado, resultado del servidor:', result);
            
            this.notification.add("✅ Prueba de notificación enviada", { 
                type: "success",
                sticky: false 
            });
            
            // ✅ AGREGAR TIMEOUT PARA VER SI LLEGA EL EVENTO
            setTimeout(() => {
                console.log('⏰ Timeout - Estado actual:', {
                    loading_response: this.state.loading_response,
                    isTesting: this.state.isTesting
                });
                if (this.state.loading_response) {
                    console.log('❌ El evento no llegó después de 3 segundos');
                    this.state.loading_response = false;
                    this.state.isTesting = false;
                }
            }, 3000);
            
        } catch (error) {
            console.error('❌ Error en testBus:', error);
            this.notification.add("❌ Error en prueba: " + error.message, { 
                type: "danger" 
            });
            this.state.loading_response = false;
            this.state.isTesting = false;
        }
    }

    // ✅ MÉTODO MEJORADO CON MÁS LOGGING
    _handleAudioResponse(ev) {
        console.log('🎯 _handleAudioResponse EJECUTADO - Estado anterior:', {
            final_message: this.state.final_message,
            answer_ia: this.state.answer_ia,
            loading_response: this.state.loading_response,
            isTesting: this.state.isTesting
        });
        
        const message = ev.detail;
        console.log('📨 Mensaje recibido en _handleAudioResponse:', message);
        
        if (message && message.type === 'new_response') {
            console.log('✅ Mensaje new_response detectado - Actualizando estado...');
            
            // ✅ ACTUALIZACIÓN EXPLÍCITA
            this.state.final_message = message.final_message || 'MENSAJE VACÍO';
            this.state.answer_ia = message.answer_ia || 'RESPUESTA VACÍA';
            this.state.loading_response = false;
            
            console.log('🔄 Estado actualizado:', {
                final_message: this.state.final_message,
                answer_ia: this.state.answer_ia,
                loading_response: this.state.loading_response
            });
            
            this.notification.add("✅ Respuesta de IA recibida via Bus", { 
                type: "success", 
                sticky: true 
            });
            
            console.log('✅ Notificación enviada y estado actualizado completamente');
        } else {
            console.log('❌ Mensaje no válido o tipo incorrecto:', message);
        }
    }

    // === MÉTODOS DE CONTACTOS ===
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