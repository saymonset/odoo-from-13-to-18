/** @odoo-module **/

  import { Component } from "@odoo/owl";
  import { registry } from "@web/core/registry";

  export class OpenAI extends Component {
      static template = "chat_bot_n8n_ia.OpenAI";
      static components = {};
      static props = {};

      setup() {}
  }

  registry.category("actions").add("chat_bot_n8n_ia.OpenAI", OpenAI);
  