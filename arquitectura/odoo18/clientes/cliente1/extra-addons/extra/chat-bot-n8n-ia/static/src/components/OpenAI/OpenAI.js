/** @odoo-module **/

  import { Component } from "@odoo/owl";
  import { registry } from "@web/core/registry";

  export class OpenAI extends Component {
      static template = "chat-bot-n8n-ia.OpenAI";
      static components = {};
      static props = {};

      setup() {}
  }

  registry.category("actions").add("chat-bot-n8n-ia.OpenAI", OpenAI);
  