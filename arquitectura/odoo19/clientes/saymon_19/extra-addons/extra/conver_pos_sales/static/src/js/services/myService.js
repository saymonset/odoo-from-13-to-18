/** @odoo-module */

import { registry } from "@web/core/registry";

export const myService = {
    dependencies: ["orm"],
    async start(env, { orm }) {

        return {  };
    },
};

registry.category("services").add("myService", myService);