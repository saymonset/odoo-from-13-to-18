/** @odoo-module **/
import { useState } from "@odoo/owl";

export class ContactManager {
    constructor(orm) {
        this.orm = orm;
        this.state = useState({
            searchTerm: "",
            availableContacts: [],
            selectedContacts: [],
        });
    }

    addContact(contact) {
        if (!this.state.selectedContacts.some(c => c.id === contact.id)) {
            this.state.selectedContacts.push(contact);
        }
        this.clearSearch();
    }

    removeContact(contactId) {
        this.state.selectedContacts = this.state.selectedContacts.filter(c => c.id !== contactId);
    }

    clearSearch() {
        this.state.searchTerm = "";
        this.state.availableContacts = [];
    }

    async searchContacts() {
        if (this.state.searchTerm.length < 2) {
            this.state.availableContacts = [];
            return;
        }

        try {
            const contacts = await this.orm.searchRead(
                "res.partner",
                [["name", "ilike", this.state.searchTerm]],
                ["name", "email", "phone"],
                { limit: 20 }
            );
            this.state.availableContacts = contacts;
        } catch (error) {
            console.error("Error buscando contactos:", error);
            this.state.availableContacts = [];
        }
    }

    getSelectedContacts() {
        return this.state.selectedContacts.map(contact => ({
            id: contact.id,
            name: contact.name,
            email: contact.email || "",
            phone: contact.phone || "",
        }));
    }

    reset() {
        this.state.selectedContacts = [];
        this.clearSearch();
    }
}
