/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";

export class VoiceRecorder extends Component {
    setup() {
        // Eliminamos el uso de useService("rpc_service")
        this.state = useState({
            recording: false,
            uploading: false,
            mediaRecorder: null,
            error: null,
        });
    }

    async toggleRecording() {
        if (!this.state.recording) {
            try {
                // Solicitar acceso al micrófono
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                const recorder = new MediaRecorder(stream);
                const chunks = [];

                recorder.ondataavailable = (e) => {
                    if (e.data.size) chunks.push(e.data);
                };

                recorder.onstop = async () => {
                    const blob = new Blob(chunks, { type: "audio/webm" });
                    const reader = new FileReader();

                    reader.onload = async () => {
                        const base64 = reader.result.split(",")[1];
                        this.state.uploading = true;
                        try {
                            // ⚡ Usamos rpc directamente
                            await rpc({
                                route: "/web/dataset/call_kw/ir.attachment/create",
                                params: {
                                    args: [{
                                        name: `voice_note_${new Date().toISOString()}.webm`,
                                        datas: base64,
                                        mimetype: "audio/webm",
                                        type: "binary",
                                    }],
                                },
                            });
                        } catch (rpcError) {
                            this.state.error = `Error al subir el audio: ${rpcError.message}`;
                        } finally {
                            this.state.uploading = false;
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
