/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PosOrder } from "@point_of_sale/app/models/pos_order";

patch(PosOrder.prototype, {
  setup(_defaultObj, options) {
    super.setup(...arguments);
    this.uso_cfdi_id = this.uso_cfdi_id || undefined;
  },

  set_uso_cfdi(uso_cfdi_id) {
    this.uso_cfdi_id = uso_cfdi_id;
  },
  get_uso_cfdio() {
    return this.uso_cfdi_id;
  },
  clean_empty_paymentlines() {
    var lines = this.paymentlines;
    this.clear_journal_amount_dict = {};
    for (var i = 0; i < lines.length; i++) {
      if (!lines[i].get_amount()) {
        this.clear_journal_amount_dict[lines[i].payment_method.id] =
          lines[i].get_amount();
      }
    }
    return super.clean_empty_paymentlines(...arguments);
  },
  export_as_JSON() {
    const json = super.export_as_JSON(...arguments);
    json.uso_cfdi_id = this.uso_cfdi_id;

    if (json.amount_return > 0.0) {
      var journal_amount_dict = {};
      var lines = this.paymentlines;
      for (var i = 0; i < lines.length; i++) {
        journal_amount_dict[lines[i].payment_method.id] = lines[i].get_amount();
      }
      if (this.clear_journal_amount_dict) {
        journal_amount_dict = [
          this.clear_journal_amount_dict,
          journal_amount_dict,
        ].reduce(function (r, o) {
          Object.keys(o).forEach(function (k) {
            r[k] = o[k];
          });
          return r;
        }, {});
      }

      json.payment_line_journals = journal_amount_dict;
    }
    return json;
  },
  export_for_printing() {
    const json = super.export_for_printing(...arguments);
    //var order = this.pos.get_order();
    json.headerData.company.regimen_fiscal_id = this.company.regimen_fiscal_id;
    json.headerData.company.zip = this.company.zip;
    json.headerData.company.nombre_fiscal = this.company.nombre_fiscal;
    json.headerData.company.street = this.company.street;
    json.headerData.company.street2 = this.company.street2;
    json.headerData.company.city = this.company.city;
    json.headerData.company.state_id = this.company.state_id;
    if (this.invoice_information) {
      json.regimen_fiscal_id = this.invoice_information.regimen_fiscal_id;
      json.regimen_fiscal = this.invoice_information.client_regime;
      json.tipo_comprobante = this.invoice_information.tipo_comprobante;
      json.folio_factura = this.invoice_information.folio_factura;
      json.client_name = this.invoice_information.client_name;
      json.client_rfc = this.invoice_information.client_rfc;
      json.uso_cfdi_id = this.invoice_information.uso_cfdi_id;
      json.methodo_pago = this.invoice_information.methodo_pago;
      json.forma_pago_id = this.invoice_information.forma_pago_id;
      json.numero_cetificado = this.invoice_information.numero_cetificado;
      json.moneda = this.invoice_information.moneda;
      json.cetificaso_sat = this.invoice_information.cetificaso_sat;
      json.tipocambio = this.invoice_information.tipocambio;
      json.folio_fiscal = this.invoice_information.folio_fiscal;
      json.fecha_certificacion = this.invoice_information.fecha_certificacion;
      json.cadena_origenal = this.invoice_information.cadena_origenal;
      json.selo_digital_cdfi = this.invoice_information.selo_digital_cdfi;
      json.selo_sat = this.invoice_information.selo_sat;
      json.invoice_id = this.invoice_information.invoice_id;
    }
    return json;
  },
  init_from_JSON(json) {
    super.init_from_JSON(...arguments);
    this.uso_cfdi_id = json.uso_cfdi_id;
  },
});
