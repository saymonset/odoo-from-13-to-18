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
            console.log("🎤 Solicitando acceso al micrófono...");
            
            // Solicitar acceso al micrófono
            this.stream = await navigator.mediaDevices.getUserMedia(AUDIO_CONSTRAINTS);
            console.log("✅ Acceso al micrófono concedido");
            
            // Crear MediaRecorder
            this.mediaRecorder = new MediaRecorder(this.stream);
            this.chunks = [];
            
            // Configurar evento para capturar datos
            this.mediaRecorder.ondataavailable = (event) => {
                console.log("📊 Datos de audio disponibles:", event.data.size, "bytes");
                if (event.data.size > 0) {
                    this.chunks.push(event.data);
                }
            };
            
            // Configurar evento cuando termina la grabación
            this.mediaRecorder.onstop = () => {
                console.log("⏹️ Grabación finalizada");
            };
            
            // Iniciar grabación con intervalos de 1000ms para asegurar datos
            this.mediaRecorder.start(1000);
            console.log("🎙️ Grabación iniciada");
            
        } catch (error) {
            console.error("❌ Error al iniciar grabación:", error);
            throw new Error(`No se pudo acceder al micrófono: ${error.message}`);
        }
    }

    async stopRecording() {
        return new Promise((resolve) => {
            if (!this.mediaRecorder || this.mediaRecorder.state === 'inactive') {
                console.warn("⚠️ No hay grabación activa para detener");
                resolve(null);
                return;
            }

            // Configurar el manejador para cuando se detenga
            this.mediaRecorder.onstop = () => {
                console.log("📦 Creando blob con", this.chunks.length, "chunks");
                const blob = new Blob(this.chunks, { type: 'audio/webm; codecs=opus' });
                console.log("🎵 Blob creado:", blob.size, "bytes");
                
                // Limpiar recursos
                this.cleanup();
                
                resolve(blob);
            };

            // Detener la grabación
            this.mediaRecorder.stop();
            console.log("🛑 Solicitando detener grabación...");
        });
    }

    cleanup() {
        // Detener todas las pistas del stream
        if (this.stream) {
            this.stream.getTracks().forEach(track => {
                console.log("🔇 Deteniendo pista:", track.kind);
                track.stop();
            });
            this.stream = null;
        }
        
        this.mediaRecorder = null;
        this.chunks = [];
    }

    isRecording() {
        return this.mediaRecorder && this.mediaRecorder.state === 'recording';
    }
}