/** @odoo-module */

import { registry } from "@web/core/registry";

export const testservice = {
    dependencies: ["orm","http","notification","action"],
    async start(env, {orm,http,notification,action }) {

        return {  };
    },
};

registry.category("services").add("testservice", testservice);