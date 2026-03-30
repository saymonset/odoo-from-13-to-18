/** @odoo-module **/
import { Component, useState, onWillStart, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";
import { useService } from "@web/core/utils/hooks";

export class PaymentProofComponent extends Component {
    static template = "conver_pos_sales.PaymentProofComponent";

    setup() {
        this.notification = useService("notification");
        this.state = useState({
            showSection: false,
            transferProviderId: null,
            fileUploading: false,
            uploadError: null,
            uploadSuccess: false,
            loading: true,      

            // Nuevos campos
            payment_date: new Date().toISOString().slice(0,10), // hoy por defecto
            payment_method: 'movil',
            bank_origin: '',
            bank_destination: 'N/A',
            reference: '',
            amount_vef: 0,
            exchange_rate: 0,
            amount_usd: 0,
            rate_date: '',
            bankList: [],   // lista de bancos para el select
        });
         onWillStart(async () => {
            this.state.loading = true;
            try {
                const providerId = await rpc("/payment_proof/get_transfer_provider_id");
                this.state.transferProviderId = providerId;
                // Obtener lista de bancos
                const banks = await rpc("/payment_proof/get_bank_list");
                this.state.bankList = banks;
                // Obtener total de la orden y tasa BCV
                const orderData = await rpc("/payment_proof/get_order_total_and_rate");
                if (orderData.error) {
                    this.notification.add(orderData.error, { type: "warning" });
                } else {
                    this.state.amount_vef = orderData.amount_vef;
                    this.state.exchange_rate = orderData.exchange_rate;
                    this.state.amount_usd = orderData.amount_usd;
                    this.state.rate_date = orderData.rate_date;
                }
            } catch (err) {
                console.error("Error inicial:", err);
                this.notification.add("Error al cargar datos de la orden", { type: "danger" });
            }finally {
                this.state.loading = false;
            }
        });
        onMounted(() => {
            console.log("✅ Componente montado");
            this._bindPaymentMethodChange();
        });

        onWillUnmount(() => {
            console.log("🔌 Desmontando componente, limpiando listeners");
            this._unbindPaymentMethodChange();
            if (this.observer) this.observer.disconnect();
        });
    }

    // Método para actualizar campos del formulario
    _updateField(event) {
        const field = event.currentTarget.dataset.field;
        let value = event.target.value;
        // Conversiones para números
        if (['amount_vef', 'exchange_rate', 'amount_usd'].includes(field)) {
            return;
        }
        this.state[field] = value;
    }

    _bindPaymentMethodChange() {
        let radioContainer = document.querySelector("div[id='payment_method']");
        if (!radioContainer) {
            radioContainer = document.querySelector(".o_payment_methods");
        }
        if (!radioContainer) {
            radioContainer = document.querySelector("[data-payment-methods]");
        }

        console.log("🔎 Contenedor de métodos de pago encontrado:", radioContainer);

        if (radioContainer) {
            radioContainer.addEventListener("change", this._onPaymentMethodChange.bind(this));
            this._onPaymentMethodChange();
        } else {
            console.warn("⚠️ No se encontró contenedor de métodos de pago, observando cambios en body");
            const targetNode = document.body;
            const config = { childList: true, subtree: true };

            this.observer = new MutationObserver((mutations, obs) => {
                let container = document.querySelector("div[id='payment_method']") ||
                                document.querySelector(".o_payment_methods") ||
                                document.querySelector("[data-payment-methods]");
                if (container) {
                    console.log("✅ Contenedor detectado dinámicamente:", container);
                    obs.disconnect();
                    container.addEventListener("change", this._onPaymentMethodChange.bind(this));
                    this._onPaymentMethodChange();
                }
            });

            this.observer.observe(targetNode, config);
        }
    }

    _unbindPaymentMethodChange() {
        const radioContainer = document.querySelector("div[id='payment_method']") ||
                               document.querySelector(".o_payment_methods") ||
                               document.querySelector("[data-payment-methods]");
        if (radioContainer) {
            radioContainer.removeEventListener("change", this._onPaymentMethodChange);
        }
    }

    _onPaymentMethodChange() {
        const selectedRadio = document.querySelector('input[name="o_payment_radio"]:checked');
        console.log("📻 Radio seleccionado:", selectedRadio);

        if (!selectedRadio) {
            console.log("❌ No hay radio seleccionado");
            this.state.showSection = false;
            return;
        }

        let providerId = selectedRadio.getAttribute("data-payment-option-id") ||
                         selectedRadio.getAttribute("data-provider-id") ||
                         selectedRadio.getAttribute("data-id") ||
                         selectedRadio.value;

        let paymentText = "";
        const label = selectedRadio.closest('label') || selectedRadio.parentElement.querySelector('label, span');
        if (label) paymentText = label.innerText.trim();
        console.log("📝 Texto del método:", paymentText);
        console.log("🆔 ID extraído del radio:", providerId);
        console.log("🏦 ID almacenado del proveedor transferencia:", this.state.transferProviderId);

        let shouldShow = false;

        if (providerId && this.state.transferProviderId && String(providerId) === String(this.state.transferProviderId)) {
            shouldShow = true;
            console.log("✅ Match por ID");
        }
        else if (paymentText) {
            const lowerText = paymentText.toLowerCase();
            if (lowerText.includes("wire transfer") || lowerText.includes("transferencia bancaria") || lowerText.includes("transferencia")) {
                shouldShow = true;
                console.log("✅ Match por texto:", paymentText);
            } else {
                console.log("❌ No match por texto");
            }
        } else {
            console.log("❌ No se pudo determinar ID ni texto");
        }

        console.log("🎯 Debe mostrar sección:", shouldShow);
        this.state.showSection = shouldShow;
    }

    async uploadFile(file) {
        this.state.fileUploading = true;
        this.state.uploadError = null;
        this.state.uploadSuccess = false;
        try {
            const formData = new FormData();
            formData.append("payment_proof_file", file);
            formData.append("payment_date", this.state.payment_date);
            formData.append("payment_method", this.state.payment_method);
            formData.append("bank_origin", this.state.bank_origin);
            formData.append("bank_destination", this.state.bank_destination);
            formData.append("reference", this.state.reference);
            formData.append("amount_vef", this.state.amount_vef);
            formData.append("exchange_rate", this.state.exchange_rate);
            formData.append("amount_usd", this.state.amount_usd);
            const response = await fetch("/shop/upload_payment_proof", {
                method: "POST",
                body: formData,
                credentials: "same-origin",
            });
            if (!response.ok) throw new Error("Error al subir el archivo");
            this.notification.add("Comprobante adjuntado correctamente.", { type: "success" });
            this.state.uploadSuccess = true;
            // Limpiar input para permitir nueva subida si se desea
            const fileInput = document.getElementById("payment_proof_file");
            if (fileInput) fileInput.value = "";
        } catch (err) {
            this.state.uploadError = err.message;
            this.notification.add("Error al adjuntar el comprobante. Intente nuevamente.", { type: "danger" });
        } finally {
            this.state.fileUploading = false;
        }
    }

    _handleFileChange(event) {
        const file = event.target.files[0];
        if (file) {
            this.uploadFile(file);
        }
    }
}

registry.category("public_components").add("conver_pos_sales.PaymentProofComponent", PaymentProofComponent);