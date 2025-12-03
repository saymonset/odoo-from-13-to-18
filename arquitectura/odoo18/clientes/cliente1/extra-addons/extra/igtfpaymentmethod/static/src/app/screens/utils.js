export const paymentMethodManager = {
  paymentMethodName: '',
  // Verificar si el IGTF es un impuesto para sumarselo al total
  _is_igtf: false,
  
  get is_igtf() {
    return this._is_igtf;
  },
  set is_igtf(value) {
    this._is_igtf = value;
  },
  // Establecer el nombre del método de pago 
  setPaymentMethodName(name) {
      this.paymentMethodName = name;
  },

  getPaymentMethodName() {
      return this.paymentMethodName;
  },
};
  