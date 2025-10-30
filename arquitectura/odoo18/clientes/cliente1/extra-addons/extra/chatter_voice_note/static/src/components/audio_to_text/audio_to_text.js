/** @odoo-module **/

  import { registry } from "@web/core/registry";
  import { Layout } from "@web/search/layout";
  import { getDefaultConfig } from "@web/views/view";

  import { Component, useSubEnv } from "@odoo/owl";

  export class Audio_to_text extends Component {
    static template = "chatter_voice_note.Audio_to_text";
    static components = { Layout };
    static props = {};

    setup() {
          useSubEnv({
              config: {
                  ...getDefaultConfig(),
                  ...this.env.config,
              },
          });
      }
  }

  registry.category("actions").add("audio_to_text", Audio_to_text);