/** @odoo-module **/
import { useState } from "@odoo/owl";

export class AudioNoteManager {
    constructor(orm, notification) {
        this.orm = orm;
        this.notification = notification;
        this.state = useState({
            notes: [],
            error: null
        });
    }

    generateTempId() {
        return `temp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    async createAudioNote(blob) {
        try {
            console.log("🎵 Creando nota de audio con blob:", blob.size, "bytes");
            
            if (!blob || blob.size === 0) {
                throw new Error("El audio grabado está vacío");
            }

            const url = URL.createObjectURL(blob);
            const name = `voice_note_${new Date().toISOString().replace(/[:.]/g, '-')}.webm`;
            const tempId = this.generateTempId();

            const newNote = {
                id: null,
                tempId,
                name,
                url,
                uploading: true,
                error: null,
                size: blob.size
            };

            this.state.notes.push(newNote);
            console.log("📝 Nota temporal creada:", newNote);
            
            await this.uploadAudio(blob, name, tempId);
            
        } catch (error) {
            console.error("❌ Error creando nota de audio:", error);
            this.notification.add("Error al crear la nota de audio", { type: "danger" });
        }
    }

    blobToBase64(blob) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result.split(",")[1]);
            reader.onerror = () => reject(new Error("Error leyendo el archivo de audio"));
            reader.readAsDataURL(blob);
        });
    }

    async uploadAudio(blob, name, tempId) {
        const noteIndex = this.state.notes.findIndex(n => n.tempId === tempId);
        if (noteIndex === -1) return;

        try {
            const base64 = await this.blobToBase64(blob);
            const attachmentId = await this.createAttachment(name, base64);
            this.updateNoteAfterUpload(noteIndex, tempId, attachmentId);
        } catch (err) {
            this.handleUploadError(noteIndex, tempId, err);
        }
    }

    async createAttachment(name, base64Data) {
        const [attachmentId] = await this.orm.create("ir.attachment", [{
            name,
            datas: base64Data,
            mimetype: "audio/webm",
            type: "binary",
            res_model: null,
            res_id: null,
        }]);
        return attachmentId;
    }

    updateNoteAfterUpload(noteIndex, tempId, attachmentId) {
        if (this.state.notes[noteIndex]?.tempId === tempId) {
            this.state.notes[noteIndex].id = attachmentId;
            this.state.notes[noteIndex].uploading = false;
            delete this.state.notes[noteIndex].tempId;
        }
    }

    handleUploadError(noteIndex, tempId, err) {
        console.error("Error subiendo audio:", err);
        const errorMsg = err.data?.message || "Error al subir el audio";
        
        if (this.state.notes[noteIndex]?.tempId === tempId) {
            this.state.notes[noteIndex].error = errorMsg;
            this.state.notes[noteIndex].uploading = false;
        }
    }

    async deleteNote(noteId) {
        if (!confirm("¿Eliminar esta nota de voz permanentemente?")) {
            return;
        }
        
        try {
            if (noteId) {
                await this.orm.unlink("ir.attachment", [noteId]);
            }
            this.state.notes = this.state.notes.filter(n => n.id !== noteId);
        } catch (err) {
            console.error("Error eliminando nota:", err);
            this.state.error = "No se pudo eliminar la nota.";
            this.notification.add("Error al eliminar la nota", { type: "danger" });
        }
    }

    getNotesForSending() {
        return this.state.notes.filter(n => n.id);
    }

    get sortedNotes() {
        return [...this.state.notes].sort((a, b) => (b.id || 0) - (a.id || 0));
    }

    reset() {
        this.state.notes = [];
    }
}