/** @odoo-module **/
import { Component, useState, onWillStart, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";

export class PaymentProofComponent extends Component {
    static template = "conver_pos_sales.PaymentProofComponent";

    setup() {
        this.state = useState({
            showSection: false,
            transferProviderId: null,
            fileUploading: false,
            uploadError: null,
        });

        // Obtener el ID del proveedor de pago que es transferencia bancaria
        onWillStart(async () => {
            try {
                const providerId = await rpc("/payment_proof/get_transfer_provider_id");
                console.log("🔍 Provider ID obtenido del backend:", providerId);
                this.state.transferProviderId = providerId;
            } catch (err) {
                console.error("❌ Error fetching transfer provider:", err);
            }
        });

        // Escuchar cambios en la selección del método de pago
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

    _bindPaymentMethodChange() {
        // Buscar el contenedor de métodos de pago. Intentar varios selectores.
        let radioContainer = document.querySelector("div[id='payment_method']");
        if (!radioContainer) {
            radioContainer = document.querySelector(".o_payment_methods");
        }
        if (!radioContainer) {
            radioContainer = document.querySelector("[data-payment-methods]");
        }

        console.log("🔎 Contenedor de métodos de pago encontrado:", radioContainer);

        if (radioContainer) {
            // Escuchar cambios en el contenedor (delegación)
            radioContainer.addEventListener("change", this._onPaymentMethodChange.bind(this));
            // Llamar una vez para establecer el estado inicial
            this._onPaymentMethodChange();
        } else {
            // Si no se encuentra, usar MutationObserver para esperar a que aparezca
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

        // Intentar obtener el ID del proveedor desde el radio seleccionado
        let providerId = selectedRadio.getAttribute("data-payment-option-id") ||
                         selectedRadio.getAttribute("data-provider-id") ||
                         selectedRadio.getAttribute("data-id") ||
                         selectedRadio.value;

        // También obtener el texto para fallback
        let paymentText = "";
        const label = selectedRadio.closest('label') || selectedRadio.parentElement.querySelector('label, span');
        if (label) paymentText = label.innerText.trim();
        console.log("📝 Texto del método:", paymentText);
        console.log("🆔 ID extraído del radio:", providerId);
        console.log("🏦 ID almacenado del proveedor transferencia:", this.state.transferProviderId);

        let shouldShow = false;

        // Primero comparar por ID si existe
        if (providerId && this.state.transferProviderId && String(providerId) === String(this.state.transferProviderId)) {
            shouldShow = true;
            console.log("✅ Match por ID");
        }
        // Si no, comparar por texto (en inglés o español)
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
        try {
            const formData = new FormData();
            formData.append("payment_proof_file", file);
            const response = await fetch("/shop/upload_payment_proof", {
                method: "POST",
                body: formData,
                credentials: "same-origin",
            });
            if (!response.ok) throw new Error("Error al subir el archivo");
            alert("Comprobante adjuntado correctamente.");
        } catch (err) {
            this.state.uploadError = err.message;
            alert("Error al adjuntar el comprobante. Intente nuevamente.");
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

// Registrar el componente para que pueda ser usado en las vistas públicas
registry.category("public_components").add("conver_pos_sales.PaymentProofComponent", PaymentProofComponent);