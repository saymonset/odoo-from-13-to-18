/** @odoo-module **/
import { Component } from "@odoo/owl";

export class ContactManagerComponent extends Component {
    static template = "chatter_voice_note.ContactManager";

    setup() {
        this.contactManager = this.props.contactManager;
    }

    onSearchInput(ev) {
        this.contactManager.state.searchTerm = ev.target.value;
        this.contactManager.searchContacts();
    }

    onAddContact(ev) {
        const id = parseInt(ev.currentTarget.dataset.contactId);
        const contact = this.contactManager.state.availableContacts.find(c => c.id === id);
        if (contact) {
            this.contactManager.addContact(contact);
        }
    }

    onRemoveContact(ev) {
        const id = parseInt(ev.currentTarget.dataset.contactId);
        this.contactManager.removeContact(id);
    }

    sendToN8N() {
        if (this.props.onSend) {
            this.props.onSend(this.contactManager.getSelectedContacts());
        }
    }
}
