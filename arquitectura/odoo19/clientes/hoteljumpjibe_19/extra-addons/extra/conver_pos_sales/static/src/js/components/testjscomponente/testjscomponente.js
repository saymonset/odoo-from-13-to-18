/** @odoo-module **/

  import { Component } from "@odoo/owl";
  import { registry } from "@web/core/registry";

  export class Testjscomponente extends Component {
      static template = "conver_pos_sales.Testjscomponente";
      static components = {};
      static props = {};

      setup() {}
  }

  registry.category("public_components").add("testjscomponente", Testjscomponente);
  