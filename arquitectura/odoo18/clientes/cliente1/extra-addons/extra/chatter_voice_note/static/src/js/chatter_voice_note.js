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
        });
         this.orm = useService("orm");
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

                    // Guardar en lista de notas
                    this.state.notes.push({
                        name: name,
                        url: url,
                        uploading: true,
                        error: null,
                    });

                    const noteIndex = this.state.notes.length - 1;

                    const reader = new FileReader();
                    reader.onload = async () => {
                        const base64 = reader.result.split(",")[1];
                        try {

                          await this.orm.create("ir.attachment", [{
                                            name: name,
                                            datas: base64,
                                            mimetype: "audio/webm",
                                            type: "binary",
                                            res_model: this.props.resModel || null,
                                            res_id: this.props.resId || null,
                                        }]);
                          this.state.notes[noteIndex].uploading = false;
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
}

VoiceRecorder.template = "chatter_voice_note.VoiceRecorder";

// Registro en OWL
registry.category("actions").add("chatter_voice_note.voice_recorder_action", VoiceRecorder);
