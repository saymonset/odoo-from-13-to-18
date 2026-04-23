/** @odoo-module **/
import { Component, useState, onWillStart, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";
import { useService } from "@web/core/utils/hooks";

export class PaymentProofComponent extends Component {
    static template = "bcv_rate_update_venezuela.PaymentProofComponent";

    setup() {
        this.notification = useService("notification");
        this.state = useState({
            showSection: false,
            transferProviderId: null,
            fileUploading: false,
            uploadError: null,
            uploadSuccess: false,
            loading: true,
            selectedFileName: null,
            proof_valid: false,

            payment_date: new Date().toISOString().slice(0, 10),
            payment_method: 'movil',
            bank_origin: '',
            bank_destination: 'N/A',
            reference: '',
            amount_vef: 0,
            exchange_rate: 0,
            amount_usd: 0,
            original_amount_vef: 0,
            original_amount_usd: 0,
            is_valid_amount: false,
            rate_date: '',
            bankList: [],
            bankJournalList: [],
            bank_details: {
                bank_name: '',
                account_number: '',
                account_holder: '',
                phone: '',
                email: '',
                routing_number: '',
                instructions: '',
                company_name: '',
                company_rif: '',
                loading: false,
                error: null,
            },
        });

        onWillStart(async () => {
            this.state.loading = true;
            try {
                const providerId = await rpc("/payment_proof/get_transfer_provider_id");
                this.state.transferProviderId = providerId;

                const banks = await rpc("/payment_proof/get_bank_list");
                this.state.bankList = banks;

                const journalBanks = await rpc("/payment_proof/get_bank_journal_list");
                this.state.bankJournalList = journalBanks;
                console.log("Bancos desde diarios contables:", journalBanks);

                const origVefSpan = document.getElementById('original_amount_vef');
                const origUsdSpan = document.getElementById('original_amount_usd');
                const rateSpan = document.getElementById('bcv_exchange_rate');
                const rateDateSpan = document.getElementById('bcv_rate_date');

                console.log("=== Spans encontrados ===");
                console.log("origVefSpan:", origVefSpan?.innerText);
                console.log("origUsdSpan:", origUsdSpan?.innerText);
                console.log("rateSpan:", rateSpan?.innerText);
                console.log("rateDateSpan:", rateDateSpan?.innerText);

                if (origVefSpan && origUsdSpan && rateSpan) {
                    this.state.original_amount_vef = parseFloat(origVefSpan.innerText) || 0;
                    this.state.original_amount_usd = parseFloat(origUsdSpan.innerText) || 0;
                    this.state.exchange_rate = parseFloat(rateSpan.innerText) || 0;
                    this.state.rate_date = rateDateSpan ? rateDateSpan.innerText : '';
                    this.state.amount_vef = this.state.original_amount_vef;
                    this.state.amount_usd = this.state.original_amount_usd;
                    console.log("Valores asignados al estado:", {
                        original_amount_vef: this.state.original_amount_vef,
                        original_amount_usd: this.state.original_amount_usd,
                        exchange_rate: this.state.exchange_rate,
                        rate_date: this.state.rate_date,
                        amount_vef: this.state.amount_vef,
                        amount_usd: this.state.amount_usd,
                    });
                    this._validateAmounts();
                } else {
                    console.warn("No se encontraron los spans con los valores originales");
                    this.notification.add("No se pudieron cargar los montos de la orden.", { type: "warning" });
                }
            } catch (err) {
                console.error("Error inicial:", err);
                this.notification.add("Error al cargar datos de la orden", { type: "danger" });
            } finally {
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

    // Normaliza números: reemplaza coma por punto y elimina caracteres no numéricos excepto punto y signo menos
    _normalizeNumber(value) {
        if (typeof value !== 'string') value = String(value);
        let cleaned = value.replace(',', '.').replace(/[^\d.-]/g, '');
        const parts = cleaned.split('.');
        if (parts.length > 2) {
            cleaned = parts[0] + '.' + parts.slice(1).join('');
        }
        const num = parseFloat(cleaned);
        return isNaN(num) ? 0 : num;
    }

    // Redondeo a 2 decimales
    _round(value) {
        return Math.round(value * 100) / 100;
    }

    // Añade este método para cargar los detalles del banco
async _loadBankDetails(journalId) {
    if (!journalId || journalId === '') {
        this.state.bank_details = {
            bank_name: '',
            account_number: '',
            account_holder: '',
            phone: '',
            email: '',
            routing_number: '',
            instructions: '',
            company_name: '',
            company_rif: '',
            loading: false,
            error: null,
        };
        return;
    }
    
    this.state.bank_details.loading = true;
    this.state.bank_details.error = null;
    
    try {
        const details = await rpc("/payment_proof/get_bank_details", {
            journal_id: journalId
        });
        
        if (details.error) {
            this.state.bank_details.error = details.error;
        } else {
            this.state.bank_details = {
                ...this.state.bank_details,
                ...details,
                loading: false,
            };
        }
    } catch (err) {
        console.error("Error cargando detalles del banco:", err);
        this.state.bank_details.error = "No se pudieron cargar los datos del banco";
        this.state.bank_details.loading = false;
    } finally {
        this.state.bank_details.loading = false;
    }
}

    _updateField(event) {
    const field = event.currentTarget.dataset.field;
    let value = event.target.value;
    this.state[field] = value;
    
    // Si es el campo bank_destination, cargar los detalles del banco
    if (field === 'bank_destination' && value) {
        this._loadBankDetails(value);
    } else if (field === 'bank_destination' && !value) {
        // Limpiar detalles si se deselecciona
        this.state.bank_details = {
            bank_name: '',
            account_number: '',
            account_holder: '',
            phone: '',
            email: '',
            routing_number: '',
            instructions: '',
            company_name: '',
            company_rif: '',
            loading: false,
            error: null,
        };
    }
}

    _onAmountVefInput(event) {
        console.log("=== _onAmountVefInput ===");
        let rawValue = event.target.value;
        let value = this._normalizeNumber(rawValue);
        console.log("Valor normalizado en Bs:", value);
        this.state.amount_vef = value;
        if (this.state.exchange_rate > 0) {
            let usd = value / this.state.exchange_rate;
            this.state.amount_usd = this._round(usd);
            console.log("USD calculado (redondeado):", this.state.amount_usd);
        } else {
            this.state.amount_usd = 0;
            console.warn("exchange_rate es 0 o negativo, no se puede convertir");
        }
        this._validateAmounts();
    }

    _onAmountUsdInput(event) {
        console.log("=== _onAmountUsdInput ===");
        let rawValue = event.target.value;
        let value = this._normalizeNumber(rawValue);
        console.log("Valor normalizado en USD:", value);
        this.state.amount_usd = value;
        if (this.state.exchange_rate > 0) {
            let vef = value * this.state.exchange_rate;
            this.state.amount_vef = this._round(vef);
            console.log("Bs calculado (redondeado):", this.state.amount_vef);
        } else {
            this.state.amount_vef = 0;
            console.warn("exchange_rate es 0 o negativo, no se puede convertir");
        }
        this._validateAmounts();
    }

    // ✅ MÉTODO PRINCIPAL DE VALIDACIÓN - Permite pagar igual o más
    _validateAmounts() {
        console.log("=== _validateAmounts ===");
        
        // Forzar conversión a número flotante
        const amountVef = parseFloat(String(this.state.amount_vef).replace(/,/g, '.')) || 0;
        const originalAmountVef = parseFloat(String(this.state.original_amount_vef).replace(/,/g, '.')) || 0;
        
        console.log("amount_vef (procesado):", amountVef);
        console.log("original_amount_vef (procesado):", originalAmountVef);
        
        // ✅ Permitir pago igual o mayor (tolerancia 0.01 por redondeo)
        const isValid = amountVef >= (originalAmountVef - 0.01);
        
        // Debug adicional
        if (amountVef > originalAmountVef) {
            console.log(`✅ Pagando más: ${amountVef} > ${originalAmountVef} - Válido`);
        } else if (Math.abs(amountVef - originalAmountVef) < 0.01) {
            console.log(`✅ Pagando exacto: ${amountVef} ≈ ${originalAmountVef} - Válido`);
        } else if (amountVef < originalAmountVef) {
            console.log(`❌ Pagando menos: ${amountVef} < ${originalAmountVef} - Inválido`);
        }
        
        console.log("¿Es válido?", isValid);
        
        this.state.is_valid_amount = isValid;
        this._checkAndTogglePaymentButton();
    }

    // Verifica ambas condiciones (monto + comprobante)
    _checkAndTogglePaymentButton() {
        const isAmountValid = this.state.is_valid_amount;
        const hasValidProof = this.state.proof_valid;
        const canEnable = isAmountValid && hasValidProof;
        
        console.log("=== Verificando condiciones para habilitar botón ===");
        console.log("Monto válido:", isAmountValid);
        console.log("Comprobante válido:", hasValidProof);
        console.log("¿Habilitar botón?", canEnable);
        
        this._togglePaymentButton(canEnable);
    }

    _togglePaymentButton(enable) {
        console.log("=== _togglePaymentButton, enable =", enable);

        const paymentButton = document.querySelector('button[name="o_payment_submit_button"]') ||
            document.querySelector('.o_payment_btn') ||
            document.querySelector('#o_payment_form button[type="submit"]') ||
            document.querySelector('.btn-primary[type="submit"]') ||
            document.querySelector('button[type="submit"]');
        
        console.log("Botón encontrado:", paymentButton);
        
        if (paymentButton) {
            if (enable) {
                paymentButton.removeAttribute('disabled');
                paymentButton.classList.remove('disabled');
                console.log("Botón habilitado");
            } else {
                paymentButton.setAttribute('disabled', 'disabled');
                paymentButton.classList.add('disabled');
                console.log("Botón deshabilitado");
            }
        } else {
            console.warn("No se encontró el botón de pago");
        }
    }

    _bindPaymentMethodChange(){
    // Buscar el contenedor de métodos de pago
    let radioContainer = document.querySelector("div[id='payment_method']");
    if (!radioContainer) {
        radioContainer = document.querySelector(".o_payment_methods");
    }
    if (!radioContainer) {
        radioContainer = document.querySelector("[data-payment-methods]");
    }
    if (!radioContainer) {
        radioContainer = document.querySelector(".payment_methods");
    }
    if (!radioContainer) {
        radioContainer = document.querySelector("#payment_method");
    }

    console.log("🔎 Contenedor de métodos de pago encontrado:", radioContainer);

    if (radioContainer) {
        // Escuchar cambios en los radios dentro del contenedor
        radioContainer.addEventListener("change", this._onPaymentMethodChange.bind(this));
        
        // También escuchar clicks en los radios por si acaso
        const radios = radioContainer.querySelectorAll('input[type="radio"]');
        radios.forEach(radio => {
            radio.addEventListener("click", this._onPaymentMethodChange.bind(this));
        });
        
        this._onPaymentMethodChange();
    } else {
        console.warn("⚠️ No se encontró contenedor de métodos de pago, observando cambios en body");
        const targetNode = document.body;
        const config = { childList: true, subtree: true };

        this.observer = new MutationObserver((mutations, obs) => {
            let container = document.querySelector("div[id='payment_method']") ||
                document.querySelector(".o_payment_methods") ||
                document.querySelector("[data-payment-methods]") ||
                document.querySelector(".payment_methods") ||
                document.querySelector("#payment_method");
            if (container) {
                console.log("✅ Contenedor detectado dinámicamente:", container);
                obs.disconnect();
                container.addEventListener("change", this._onPaymentMethodChange.bind(this));
                
                const radios = container.querySelectorAll('input[type="radio"]');
                radios.forEach(radio => {
                    radio.addEventListener("click", this._onPaymentMethodChange.bind(this));
                });
                
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
            // Buscar el método de pago seleccionado de diferentes maneras
            let selectedRadio = document.querySelector('input[name="o_payment_radio"]:checked');
            
            // Si no encuentra, buscar por otros nombres comunes
            if (!selectedRadio) {
                selectedRadio = document.querySelector('input[name="payment_method"]:checked');
            }
            if (!selectedRadio) {
                selectedRadio = document.querySelector('input[type="radio"][name*="payment"]:checked');
            }
            if (!selectedRadio) {
                selectedRadio = document.querySelector('.o_payment_methods input[type="radio"]:checked');
            }
            
            console.log("📻 Radio seleccionado:", selectedRadio);

            if (!selectedRadio) {
                console.log("❌ No hay radio seleccionado");
                this.state.showSection = false;
                return;
            }

            // Obtener el provider ID de diferentes atributos posibles
            let providerId = selectedRadio.getAttribute("data-payment-option-id") ||
                selectedRadio.getAttribute("data-provider-id") ||
                selectedRadio.getAttribute("data-id") ||
                selectedRadio.value;

            // Obtener el texto del método de pago
            let paymentText = "";
            const label = selectedRadio.closest('label') || 
                        selectedRadio.parentElement.querySelector('label, span') ||
                        selectedRadio.parentElement;
            if (label) paymentText = label.innerText.trim();
            
            // También buscar en el contenedor padre
            const parentDiv = selectedRadio.closest('.payment_method');
            if (parentDiv) {
                const titleElem = parentDiv.querySelector('.payment_method_title, .method-name, h4, strong');
                if (titleElem) paymentText = titleElem.innerText.trim();
            }
            
            console.log("📝 Texto del método:", paymentText);
            console.log("🆔 ID extraído del radio:", providerId);
            console.log("🏦 ID almacenado del proveedor transferencia:", this.state.transferProviderId);

            let shouldShow = false;

            // Comparar por ID
            if (providerId && this.state.transferProviderId && String(providerId) === String(this.state.transferProviderId)) {
                shouldShow = true;
                console.log("✅ Match por ID");
            }
            // Comparar por texto
            else if (paymentText) {
                const lowerText = paymentText.toLowerCase();
                if (lowerText.includes("wire transfer") || 
                    lowerText.includes("transferencia bancaria") || 
                    lowerText.includes("transferencia") ||
                    lowerText.includes("bank transfer") ||
                    lowerText.includes("wire")) {
                    shouldShow = true;
                    console.log("✅ Match por texto:", paymentText);
                } else {
                    console.log("❌ No match por texto");
                }
            } 
            // Si todo falla, mostrar para depuración
            else {
                console.log("❌ No se pudo determinar ID ni texto");
                // Opcional: Mostrar para debugging
                console.log("HTML del radio:", selectedRadio.outerHTML);
            }

            console.log("🎯 Debe mostrar sección:", shouldShow);
            this.state.showSection = shouldShow;
        }

    async uploadFile(file) {
        this.state.fileUploading = true;
        this.state.uploadError = null;
        this.state.uploadSuccess = false;
        this.state.proof_valid = false;
        
        // Deshabilita el botón mientras sube
        this._togglePaymentButton(false);
        
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
            this.state.proof_valid = true;
            
            // Re-evalúa las condiciones (ahora el comprobante es válido)
            this._checkAndTogglePaymentButton();
            
        } catch (err) {
            this.state.uploadError = err.message;
            this.state.proof_valid = false;
            this.notification.add("Error al adjuntar el comprobante. Intente nuevamente.", { type: "danger" });
            
            // Asegura que el botón siga deshabilitado
            this._togglePaymentButton(false);
        } finally {
            this.state.fileUploading = false;
        }
    }

    _handleFileChange(event) {
        const file = event.target.files[0];
        if (file) {
            this.state.selectedFileName = file.name;
            this.state.proof_valid = false;
            this.state.uploadSuccess = false;
            this.state.uploadError = null;
            this._togglePaymentButton(false);
            this.uploadFile(file);
        } else {
            this.state.selectedFileName = null;
            this.state.proof_valid = false;
            this.state.uploadSuccess = false;
            this._checkAndTogglePaymentButton();
        }
    }
}

registry.category("public_components").add("bcv_rate_update_venezuela.PaymentProofComponent", PaymentProofComponent);