/** @odoo-module **/
import { registry } from "@web/core/registry";

// Servicio de bus básico - se usará a través de useService
const busService = {
    dependencies: ["bus_service"],
    start(env, { bus_service }) {
        return bus_service;
    },
};

registry.category("services").add("custom_bus_service", busService);