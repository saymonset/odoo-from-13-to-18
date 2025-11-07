/** @odoo-module **/
import { AUDIO_CONSTRAINTS } from "./constants";

export class AudioRecorder {
    constructor() {
        this.mediaRecorder = null;
        this.stream = null;
        this.chunks = [];
    }

    async startRecording() {
        try {
            console.log("Solicitando micrófono...");
            this.stream = await navigator.mediaDevices.getUserMedia(AUDIO_CONSTRAINTS);
            console.log("Micrófono concedido");

            this.mediaRecorder = new MediaRecorder(this.stream);
            this.chunks = [];

            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.chunks.push(event.data);
                }
            };

            this.mediaRecorder.start();
            console.log("Grabación iniciada");

        } catch (error) {
            console.error("Error micrófono:", error);
            throw new Error("No se pudo acceder al micrófono");
        }
    }

    async stopRecording() {
        return new Promise((resolve) => {
            if (!this.mediaRecorder || this.mediaRecorder.state === 'inactive') {
                resolve(null);
                return;
            }

            this.mediaRecorder.onstop = () => {
                const blob = new Blob(this. chunks, { type: 'audio/webm' });
                this.cleanup();
                resolve(blob);
            };

            this.mediaRecorder.stop();
        });
    }

    cleanup() {
        if (this.stream) {
            this.stream.getTracks().forEach(t => t.stop());
            this.stream = null;
        }
        this.mediaRecorder = null;
        this.chunks = [];
    }
}