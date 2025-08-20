/** @odoo-module **/

import { Component } from "@odoo/owl";

export class ColumnProgress extends Component {
  static template = "delivery_orders_report.ColumnProgress";
  static components = {};
  // Propiedades del componente
  static props = {
    group: Object,
    progressBar: Number,
    aggregate: String,
    onBarClicked: Function,
  };

  // Método que se ejecuta al hacer clic en la barra
  onBarClicked() {
    this.props.onBarClicked(this.props.group);
  }

  setup() {}
}
