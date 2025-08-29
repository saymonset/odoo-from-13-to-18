/** @odoo-module **/

  import { Component } from "@odoo/owl";
  import { registry } from "@web/core/registry";

  export class OpenAI extends Component {
      static template = "react-odoo.OpenAI";
      static components = {};
      static props = {};

      setup() {}
  }

  registry.category("actions").add("react-odoo.OpenAI", OpenAI);
  