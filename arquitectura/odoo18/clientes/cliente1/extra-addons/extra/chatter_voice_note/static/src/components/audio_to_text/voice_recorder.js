/** @odoo-module **/
import { Component, useState, onWillUnmount, markup } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { ContactManager } from "./contact_manager";
import { ContactManagerComponent } from "./contact_manager_component";
import { AudioRecorder } from "./audio_recorder";
import { AudioNoteManager } from "./audio_note_manager";
import { MedicalReport } from "./medical_report";
import { N8NService } from "./n8n_service";


export class VoiceRecorder extends Component {
    static template = "chatter_voice_note.VoiceRecorder";
    static components = {
        ContactManagerComponent,
        MedicalReport
    };

    setup() {


         
        
        this.initServices();
        this.initManagers();

        this.contactManager = new ContactManager(this.orm);
        
        // ESTADO SIMPLIFICADO
        this.state = useState({
            recording: false,
            isSending: false,
            final_message: '',
            answer_ia: '',
            debugInfo: 'Sistema listo',
            error: null,
            // 🔥 ESTADOS PARA EDICIÓN
            editingFinalMessage: false,
            editedFinalMessage: '',
            showMedicalReport: false,
            reportUserData: null,
            reportTitle: 'Reporte Médico'

        });
        
        this.currentRequestId = null;
        this.pollInterval = null; 

        onWillUnmount(() =>{
            this.stopPolling(); // ← SIEMPRE
            this.cleanup()
        } );
    }

    // 🔥 POLLING INTELIGENTE (SIN BUS, SIN POLLING CONSTANTE)
startPollingWhenNeeded() {
    if (this.currentRequestId && !this.state.final_message) {
        this.startPolling();
    }
}

startPolling() {
    if (this.pollInterval) return;

    this.pollInterval = setInterval(async () => {
        if (!this.currentRequestId || this.state.final_message) {
            this.stopPolling();
            return;
        }

        try {
            const res = await this.tryControllerCall(this.currentRequestId);
            if (res && res.found && res.final_message) {
                console.log("RESPUESTA ENCONTRADA EN POLLING:", res);
                this.processResponse(res);
                this.stopPolling();
            }
        } catch (err) {
            console.warn("Polling error (continúa):", err);
        }
    }, 3000);
}

stopPolling() {
    if (this.pollInterval) {
        clearInterval(this.pollInterval);
        this.pollInterval = null;
    }
}

    initServices() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        console.log("✅ Servicios cargados");
    }

    initManagers() {
        this.contactManager = new ContactManager(this.orm);
        this.audioRecorder = new AudioRecorder();
        this.audioNoteManager = new AudioNoteManager(this.orm, this.notification);
        this.n8nService = new N8NService(this.orm, this.notification);
    }

     // 🔥 MÉTODOS DE EDICIÓN DEL MENSAJE FINAL
    startEditingFinalMessage() {
        console.log("✏️ Iniciando edición del mensaje final");
        this.state.editedFinalMessage = this.state.final_message;
        this.state.editingFinalMessage = true;
    }

    async getUserData() {
                try {
                    const result = await this.orm.call("res.users", "get_current_user_info", [], {});
                    console.log("👤 Datos del usuario obtenidos vía RPC:", result);
                    return result;
                } catch (error) {
                    console.error("❌ Error al obtener usuario:", error);
                    return {
                        name: "Usuario desconocido",
                        userId: null,
                    };
                }
            }


       
    async saveFinalMessage() {
        console.log("💾 Guardando mensaje final editado");
        this.state.final_message = this.state.editedFinalMessage;
        this.state.editingFinalMessage = false;

           // 🔥 OBTENER DATOS DEL USUARIO Y PASARLOS AL REPORTE
        const userData = await this.getUserData();
        console.log("🔍 Datos de usuario que se enviarán al reporte:", userData);
        this.state.reportUserData = userData;
         // 🔥 MOSTRAR REPORTE AUTOMÁTICAMENTE
        this.state.showMedicalReport = true;
        this.state.reportUserData = userData;
        this.state.reportContacts = this.contactManager.state.selectedContacts; 
        
        this.notification.add(
            "✅ Mensaje final actualizado correctamente",
            { type: "success" }
        );
    }

    // CERRAR REPORTE
    closeMedicalReport = () => {
        console.log("🔴 Cerrando reporte médico");
        this.state.showMedicalReport = false;
    }

      // 🔥  MÉTODO PARA FORMATEAR CONTENIDO
     get formattedReportContent() {
        if (!this.state.final_message) return markup('');
        
        const htmlContent = this.state.final_message
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>');
            
        return markup(htmlContent); // 🔥 ENVOLVER CON markup
    }


    cancelEditingFinalMessage() {
        console.log("❌ Cancelando edición del mensaje final");
        this.state.editingFinalMessage = false;
        this.state.editedFinalMessage = '';
        
        this.notification.add(
            "Edición cancelada",
            { type: "info" }
        );
    }

    // 🔥 MÉTODOS DE MANEJO DE EVENTOS SIMPLIFICADOS
    onSearchInput(ev) {
        this.contactManager.state.searchTerm = ev.target.value;
        this.contactManager.searchContacts();
    }

    onAddContact(ev) {
        const contactId = parseInt(ev.currentTarget.dataset.contactId);
        const contact = this.contactManager.state.availableContacts.find(c => c.id === contactId);
        if (contact) {
            this.contactManager.addContact(contact);
        }
    }

    onRemoveContact(ev) {
        const contactId = parseInt(ev.currentTarget.dataset.contactId);
        this.contactManager.removeContact(contactId);
    }

    deleteNote(ev) {
        const noteId = parseInt(ev.currentTarget.dataset.noteId);
        this.audioNoteManager.deleteNote(noteId);
    }

generateUniqueRequestId() {
    // 1. Timestamp en milisegundos
    const timestamp = Date.now();
    
    // 2. ID del usuario actual (si está logueado)
    const userId = this.env.user?.id || 0;
    
    // 3. Generar UUID v4 simple (sin librerías)
    const uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
    
    // 4. Combinar todo
    return `req_${userId}_${timestamp}_${uuid.substring(0, 8)}`;
}

 async sendToN8N() {
    const notes = this.audioNoteManager.getNotesForSending();
    const contacts = this.contactManager.getSelectedContacts();

    if (notes.length === 0) {
        this.notification.add("Graba un audio primero", { type: "warning" });
        return;
    }

    // GENERAR ID ÚNICO SEGURO
    this.currentRequestId = this.generateUniqueRequestId();
    this.state.isSending = true;
     // 🔥 LIMPIAR ESTADOS DE EDICIÓN AL ENVIAR NUEVA SOLICITUD
    this.state.editingFinalMessage = false;
    this.state.editedFinalMessage = '';
    this.state.showMedicalReport = false; 
    this.state.final_message = '';          
    this.state.answer_ia = '';              

    try {
        await this.n8nService.sendToN8N(
            notes,
            contacts,
            this.props.resModel,
            this.props.resId,
            this.currentRequestId
        );
        this.startPollingWhenNeeded(); // INICIA POLLING
    } catch (err) {
        console.error("Error envío:", err);
        this.state.isSending = false; 
        this.state.debugInfo = 'Error al enviar';
        this.notification.add("Error al enviar el audio", { type: "danger" });
    } finally {
    }
}

    // 🔥 VERIFICAR RESPUESTA MANUALMENTE
    async checkResponse() {
        if (!this.currentRequestId) {
            this.notification.add("No hay solicitud activa para verificar", { type: "info" });
            return;
        }

        this.state.debugInfo = 'Verificando respuesta...';
        
        try {
            const response = await this.tryControllerCall(this.currentRequestId);
            
            if (response && response.final_message) {
                console.log("✅ RESPUESTA ENCONTRADA:", response);
                this.processResponse(response);
                this.stopPolling(); // ← DETIENE AL RECIBIR RESPUESTA
            } else {
                this.state.debugInfo = 'Respuesta aún no disponible';
                this.notification.add("La respuesta aún no está disponible. Intenta más tarde.", { 
                    type: "info" 
                });
            }
            
        } catch (error) {
            console.error("❌ Error verificando respuesta:", error);
            this.state.debugInfo = `Error: ${error.message}`;
            this.notification.add(`Error al verificar: ${error.message}`, { type: "danger" });
        }
    }

    // 🔥 LLAMADA DIRECTA AL CONTROLADOR

    async tryControllerCall(requestId) {
            try {
                console.log("Buscando respuesta via controlador para:", requestId);
                
                const payload = { request_id: requestId };

                const response = await fetch('/chatter_voice_note/get_response', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    body: JSON.stringify(payload)
                });
                
                if (!response.ok) {
                    console.warn("HTTP error:", response.status);
                    return null;
                }

                const data = await response.json();
                console.log("Respuesta cruda:", data);

                // DESENVOLVER JSON-RPC
                if (data.jsonrpc === '2.0' && data.result) {
                    const result = data.result;
                    console.log("Respuesta procesada:", result);
                    return result;
                } else {
                    console.warn("Formato JSON-RPC inválido:", data);
                    return null;
                }
                
            } catch (error) {
                console.error("Error en fetch:", error);
                return null;
            }
        }

    // 🔥 PROCESAR RESPUESTA
    processResponse(payload) {
        this.state.final_message = String(payload.final_message);
        this.state.answer_ia = String(payload.answer_ia || '');
        this.state.debugInfo = 'Procesamiento completado ✓';
        this.state.error = null;

        this.state.isSending = false;

         // 🔥 INICIAR AUTOMÁTICAMENTE EN MODO EDICIÓN
        this.state.editedFinalMessage = this.state.final_message;
        this.state.editingFinalMessage = true;
        
        this.notification.add(
            `✅ Procesamiento completado: ${payload.final_message.substring(0, 40)}...`,
            { type: "success" }
        );
        
     
    }

    cleanup() {
        if (this.state.recording) {
            this.audioRecorder.cleanup();
        }
    }

    // 🔥 RESET DE INTERFAZ
    resetInterface() {
        this.audioNoteManager.reset();
        this.contactManager.reset();
        this.currentRequestId = null;
        this.state.final_message = '';
        this.state.answer_ia = '';
        this.state.debugInfo = 'Sistema listo para nueva consulta';
        this.state.error = null;
        this.state.editingFinalMessage = false;
        this.state.editedFinalMessage = '';
        this.state.showMedicalReport = false;  
        this.state.isSending = false; 
        this.stopPolling(); 
    }

    async toggleRecording() {
        if (this.state.recording) {
            await this.stopRecording();
            // 🔥 AUTOMÁTICAMENTE PROCESAR AL TERMINAR LA GRABACIÓN
            await this.sendToN8N();
        } else {
            await this.startRecording();
        }
    }

    async startRecording() {
        try {
            // RESetea solo cuando se inicia una NUEVA grabación
            this.resetInterface();  // ← ¡AQUÍ!
            await this.audioRecorder.startRecording();
            this.state.recording = true;
            this.state.error = null;
        } catch (err) {
            this.state.error = err.message;
            this.state.recording = false;
        }
    }

    // ... resto del código igual ...

async stopRecording() {
    try {
        const blob = await this.audioRecorder.stopRecording();
        this.state.recording = false;

        if (blob && blob.size > 0) {
            const url = URL.createObjectURL(blob);
            await this.audioNoteManager.createAudioNote({ blob, url });
        }
    } catch (err) {
        this.state.error = err.message;
    }
}

    get sortedNotes() {
        return this.audioNoteManager.sortedNotes;
    }
}