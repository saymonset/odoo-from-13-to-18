/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";
import { useService } from "@web/core/utils/hooks";

export class VoiceRecorder extends Component {
        setup() {
        this.state = useState({
            recording: false,
            uploading: false,
            mediaRecorder: null,
            notes: [],  // Lista de notas grabadas
            error: null,
            isSending: false,
            searchTerm: '',  // Término de búsqueda para contactos
            availableContacts: [],  // Contactos disponibles para selección
            selectedContacts: [],  // Contactos seleccionados
        });
         this.orm = useService("orm");
    }

    /**
 * Agrega un contacto a la lista de contactos seleccionados.
 * @param {Object} contact - El contacto a agregar.
 */
addContact= (contact) =>{
    // Evitar duplicados
    if (!this.state.selectedContacts.some(c => c.id === contact.id)) {
        this.state.selectedContacts.push(contact);
    }
    // Limpiar el término de búsqueda y los contactos disponibles después de agregar
    this.state.searchTerm = '';
    this.state.availableContacts = [];
}

/**
 * Quita un contacto de la lista de contactos seleccionados.
 * @param {number} contactId - El ID del contacto a quitar.
 */
removeContact  = (contactId) => {
    this.state.selectedContacts = this.state.selectedContacts.filter(c => c.id !== contactId);
}
     /**
     * Propiedad computada para ordenar las notas.
     * Ordena las notas por 'id' de forma descendente (mayor a menor),
     * asumiendo que el 'id' es el ID de Odoo (ir.attachment) y que un ID
     * más alto significa una creación más reciente.
     */
    get sortedNotes() {
        // Hacemos una copia para no mutar el array original en state
        // Si la nota aún no tiene ID (aún no se ha subido), la ponemos al final temporalmente (id = 0)
        return [...this.state.notes].sort((a, b) => (b.id || 0) - (a.id || 0));
    }

    /**
     * Elimina la nota seleccionada del estado local y de la base de datos de Odoo.
     * @param {number} noteId - El ID del registro ir.attachment a eliminar.
     */
    async deleteNote(noteId) {
        if (!noteId) {
            // Esto no debería pasar si se ha subido correctamente, pero es una buena práctica.
            console.warn("Intento de eliminar una nota sin ID de Odoo.");
            this.state.notes = this.state.notes.filter(note => note.id !== noteId);
            return;
        }

        if (!confirm("¿Está seguro de que desea eliminar permanentemente esta nota de voz?")) {
            return;
        }

        try {
            // 1. Eliminar de la base de datos (ir.attachment)
            await this.orm.unlink("ir.attachment", [noteId]);

            // 2. Si tiene éxito, eliminar del estado local
            this.state.notes = this.state.notes.filter(note => note.id !== noteId);

            // Mostrar notificación de éxito

        } catch (error) {
            console.error("Error al eliminar la nota en el servidor:", error);
            // Mostrar notificación de error
        }
    }

/**
     * Busca contactos en Odoo basados en el término de búsqueda.
     */
    async searchContacts() {
        if (this.state.searchTerm.length < 2) {
            this.state.availableContacts = [];
            return;
        }
        try {
            const domain = [['name', 'ilike', this.state.searchTerm]];
            const fields = ['name', 'email', 'phone'];  // Campos a recuperar (puedes agregar más si necesitas)
            const contacts = await this.orm.searchRead('res.partner', domain, fields, { limit: 20 });
            this.state.availableContacts = contacts;
        } catch (error) {
            console.error("Error al buscar contactos:", error);
            this.state.error = "Error al buscar contactos.";
        }
    }

    async toggleRecording() {
        if (!this.state.recording) {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                const recorder = new MediaRecorder(stream);
                const chunks = [];

                recorder.ondataavailable = (e) => {
                    if (e.data.size) chunks.push(e.data);
                };

                recorder.onstop = async () => {
                    const blob = new Blob(chunks, { type: "audio/webm" });
                    const url = URL.createObjectURL(blob);  // URL para reproducir
                    const name = `voice_note_${new Date().toISOString()}.webm`;
                    const tempId = Date.now(); // ID temporal para rastrear el elemento


                       // Guardar en lista de notas con un ID temporal
                    this.state.notes.push({
                        id: null, // El ID real de Odoo se asignará al subir
                        tempId: tempId,
                        name: name,
                        url: url,
                        uploading: true,
                        error: null,
                    });


                    
                    // Usamos el tempId para encontrar la nota que estamos subiendo
                    const noteIndex = this.state.notes.findIndex(note => note.tempId === tempId);


                    const reader = new FileReader();
                    reader.onload = async () => {
                        const base64 = reader.result.split(",")[1];
                        try {

                         const [attachmentId] = await this.orm.create("ir.attachment", [{
                                            name: name,
                                            datas: base64,
                                            mimetype: "audio/webm",
                                            type: "binary",
                                            res_model: this.props.resModel || null,
                                            res_id: this.props.resId || null,
                                        }]);
                           // Actualizar el estado de la nota con el ID real y quitar el 'uploading'
                            if (noteIndex !== -1) {
                                this.state.notes[noteIndex].id = attachmentId; // <<< AQUI SE GUARDA EL ID REAL
                                this.state.notes[noteIndex].uploading = false;
                                delete this.state.notes[noteIndex].tempId; // Limpiamos el ID temporal
                            } 
                        } catch (rpcError) {
                            console.error("Error en RPC:", rpcError); // Imprimir el error completo para depuración
                            let errorMessage = "Error al subir el archivo.";
                            if (rpcError.data && rpcError.data.message) {
                                errorMessage = `Error al subir: ${rpcError.data.message}`;
                            } else if (rpcError.message) {
                                errorMessage = `Error al subir: ${rpcError.message}`;
                            }
                            this.state.notes[noteIndex].error = errorMessage;
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
                this.state.error = `No se pudo acceder al micrófono: ${err.message}`;
            }
        } else {
            this.state.mediaRecorder.stop();
            this.state.recording = false;
        }
    }

    /**
     * Envía todas las notas grabadas a la URL del webhook de n8n.
     */
    async sendToN8N() {
        const N8N_WEBHOOK_URL = "https://n8n.jumpjibe.com/webhook/audios";

        // Filtrar solo las notas que se hayan subido correctamente (tienen un ID de Odoo)
        const notesToSend = this.state.notes.filter(note => note.id);

      //  if (notesToSend.length === 0) {
        if (notesToSend.length === 0 && this.state.selectedContacts.length === 0) {
            //this.notification.add("No hay notas de voz grabadas y subidas para enviar.", { type: "info" });
            alert("No hay notas de voz ni contactos seleccionados para enviar.");
            return;
        }

        this.state.isSending = true;

        try {
            // 1. Obtener los datos binarios (base64) de Odoo
            //const attachmentIds = notesToSend.map(note => note.id);
            
            // Buscar los adjuntos y seleccionar los campos que necesitamos
            // 'datas' es el campo binario (base64) que queremos enviar
            //const attachments = await this.orm.read("ir.attachment", attachmentIds, ["name", "datas", "mimetype", "res_id", "res_model"]);

            // 1. Obtener los datos binarios (base64) de los audios
            let audios = [];
            if (notesToSend.length > 0) {
                const attachmentIds = notesToSend.map(note => note.id);
                const attachments = await this.orm.read("ir.attachment", attachmentIds, ["name", "datas", "mimetype", "res_id", "res_model"]);
                audios = attachments.map(att => ({
                    filename: att.name,
                    mimetype: att.mimetype,
                    data: att.datas,
                }));
            }

           // 2. Formatear la data para n8n, incluyendo los contactos seleccionados
            const payload = {
                record_id: this.props.resId || null,
                model: this.props.resModel || null,
                audios: audios,
                contacts: this.state.selectedContacts.map(contact => ({
                    id: contact.id,
                    name: contact.name,
                    email: contact.email || '',
                    phone: contact.phone || '',
                })),
            };

            // 3. Enviar la petición POST a n8n
            const response = await fetch(N8N_WEBHOOK_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });

            if (response.ok) {
              //  this.notification.add(`Notas enviadas con éxito a n8n. (${notesToSend.length} archivos)`, { type: "success" });
               // alert(`Notas enviadas con éxito a n8n. (${notesToSend.length} archivos)`);
               alert(`Datos enviados con éxito a n8n. (${notesToSend.length} audios, ${this.state.selectedContacts.length} contactos)`);
                // OPCIONAL: Si quieres borrar las notas locales después de enviar
                this.state.notes = []; 
                this.state.selectedContacts = [];
            } else {
                const errorText = await response.text();
                alert(`Error al enviar a n8n: ${response.status} - ${errorText.substring(0, 100)}`);
                //this.notification.add(`Error al enviar a n8n: ${response.status} - ${errorText.substring(0, 100)}`, { type: "danger" });
            }

        } catch (error) {
            console.error("Error en la conexión o proceso de envío:", error);
            alert("Ocurrió un error de red o interno al enviar las notas.");
            //this.notification.add("Ocurrió un error de red o interno al enviar las notas.", { type: "danger" });
        } finally {
            this.state.isSending = false;
        }
    }
}

VoiceRecorder.template = "chatter_voice_note.VoiceRecorder";

// Registro en OWL
registry.category("actions").add("chatter_voice_note.voice_recorder_action", VoiceRecorder);
