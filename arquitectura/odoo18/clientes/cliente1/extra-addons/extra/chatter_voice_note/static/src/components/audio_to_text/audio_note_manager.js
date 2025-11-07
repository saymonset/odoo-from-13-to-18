/** @odoo-module **/

export class AudioNoteManager {
    constructor(orm, notification) {
        this.orm = orm;
        this.notification = notification;
        this.state = { notes: [] };
        this.nextId = 1;
    }

    async createAudioNote({ blob, url }) {
        const note = {
            id: this.nextId++,
            name: `Nota ${new Date().toLocaleTimeString()}`,
            url,
            blob,
            filename: `audio_${Date.now()}.webm`
        };
        this.state.notes.push(note);
        this.notification.add("Grabación guardada", { type: "success" });
    }

    deleteNote(noteId) {
        const index = this.state.notes.findIndex(n => n.id === noteId);
        if (index !== -1) {
            URL.revokeObjectURL(this.state.notes[index].url);
            this.state.notes.splice(index, 1);
            this.notification.add("Nota eliminada", { type: "info" });
        }
    }

    getNotesForSending() {
        return this.state.notes.map(note => ({
            data: note.blob,
            filename: note.filename
        }));
    }

    get sortedNotes() {
        return [...this.state.notes].reverse();
    }

    reset() {
        this.state.notes.forEach(n => URL.revokeObjectURL(n.url));
        this.state.notes = [];
        this.nextId = 1;
    }
}