/** @odoo-module **/

import { patch } from '@web/core/utils/patch';
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import {  onMounted, onWillStart , onWillUpdateProps } from "@odoo/owl";
import {  paymentMethodManager } from "@igtfpaymentmethod/app/screens/utils";
import { _t } from "@web/core/l10n/translation";
import { useService} from "@web/core/utils/hooks"
const originalAddNewPaymentLine = PaymentScreen.prototype.addNewPaymentLine;

patch(PaymentScreen.prototype, {
  components: {
    ...PaymentScreen.components,
},
  setup() {
    super.setup(...arguments);
    this.igtfPaymentScreenService = useService("igtfPaymentScreenService");

    onWillStart(() => {
        this.igtfPaymentScreenService.setCurrentOrder(this.currentOrder);
    });
    onWillUpdateProps((nextProps) => {
        this.igtfPaymentScreenService.setCurrentOrder(nextProps.currentOrder);
    });
},

async deletePaymentLine(uuid) {
  // Llama al método original para mantener la funcionalidad existente
  const line = this.paymentLines.find((line) => line.uuid === uuid);
  // Agrega tu lógica adicional aquí
  if (line) {
              // Si el método de pago es QR Code, maneja la eliminación
              if (line.payment_method_id.payment_method_type === "qr_code") {
                  this.currentOrder.remove_paymentline(line);
                  this.numberBuffer.reset();
                  return;
              }

              // Manejo de cancelación para pagos en espera
              if (["waiting", "waitingCard", "timeout"].includes(line.get_payment_status())) {
                  line.set_payment_status("waitingCancel");
                  await line.payment_method_id.payment_terminal.send_payment_cancel(this.currentOrder, uuid);
              }

              // Elimina la línea de pago
              this.currentOrder.remove_paymentline(line);
              this.numberBuffer.reset();
               // Actualiza el nombre del método de pago en el servicio
               paymentMethodManager.setPaymentMethodName("");
               paymentMethodManager.is_igtf=false;
  }
},
    
    /**
     * Sobrescribimos el método para agregar un manejador de clic personalizado.
     */
   async addNewPaymentLine(paymentMethod) {
          // Guarda el nombre del método de pago en el servicio
          paymentMethodManager.setPaymentMethodName(paymentMethod.name);
          paymentMethodManager.is_igtf=paymentMethod.is_igtf;
        // Llama al método original para que continúe con su funcionalidad
          originalAddNewPaymentLine.call(this, paymentMethod);
        
        // Verifica si el método de pago es IGTF y aplica el 30%
        if (paymentMethod.is_igtf) {
          // Obtén la última línea de pago
          const paymentLines = this.paymentLines;
          if (paymentLines.length > 0) {
              // Supongamos que paymentMethod es un objeto que ya existe
            const percentageString = ` (${paymentMethod.igtf_percentage}%)`;
              // Verifica si el nombre ya contiene la concatenación
            if (!paymentMethod.name.includes(percentageString)) {
              // Si no está presente, concatena el porcentaje al nombre
              paymentMethod.name += percentageString;
            }
            const lastLine = paymentLines[paymentLines.length - 1];
            lastLine.amount = (( paymentMethod.igtf_percentage / 100) * (this.currentOrder.getTotalDue() || 0) ) * -1 // Update the value of the last element
          }
      }
    },
});
