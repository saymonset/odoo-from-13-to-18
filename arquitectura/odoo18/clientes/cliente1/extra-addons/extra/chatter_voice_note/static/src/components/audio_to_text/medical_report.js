/** @odoo-module **/
import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class MedicalReport extends Component {
    static template = "chatter_voice_note.MedicalReport";
    static props = {
        content: String,
        title: { type: String, optional: true },
        onClose: { type: Function, optional: true },
        userData: { type: Object, optional: true },
        contacts: { type: Array, optional: true },
        resModel: { type: String, optional: true },
        resId: { type: Number, optional: true },
    };

    setup() {
        super.setup();
        this.notification = useService("notification");
        this.orm = useService("orm");

        this.state = useState({
            companyLogo: null,
            companyName: '',
            userName: 'Dr. Médico',
            userJobTitle: 'Especialista'
        });

        this.loadCompanyData();
        this.setUserDataFromProps();
    }

    // ==================================================================
    // CARGA DE DATOS
    // ==================================================================
    async loadCompanyData() {
        try {
            const companies = await this.orm.searchRead("res.company", [], ["logo", "name"], { limit: 1 });
            if (companies?.length) {
                this.state.companyLogo = companies[0].logo || null;
                this.state.companyName = companies[0].name || "CENTRO MÉDICO";
            }
        } catch (err) {
            console.warn("Error cargando datos de compañía", err);
        }
    }

    setUserDataFromProps() {
        if (this.props.userData?.name) {
            this.state.userName = this.props.userData.name;
            if (this.props.userData.userId) this.loadUserDetailsFromDB(this.props.userData.userId);
        }
        this.enhanceUserData();
    }

    async loadUserDetailsFromDB(userId) {
        try {
            const users = await this.orm.searchRead("res.users", [["id", "=", userId]], ["name", "job_id"], { limit: 1 });
            if (users?.length && users[0].job_id) {
                this.state.userJobTitle = users[0].job_id[1];
            }
        } catch (err) { /* silencioso */ }
        this.enhanceUserData();
    }

    enhanceUserData() {
        if (this.state.userName && !/^Dr(a|\.)?\s/i.test(this.state.userName)) {
            const lastName = this.state.userName.trim().split(" ").pop();
            this.state.userName = `Dr. ${lastName}`;
        }
    }

    // ==================================================================
    // UTILIDADES
    // ==================================================================
    get currentDate() {
        return new Date().toLocaleDateString('es-ES', { year: 'numeric', month: 'long', day: 'numeric' });
    }

    get currentDateTime() {
        return new Date().toLocaleString('es-ES', {
            year: 'numeric', month: 'long', day: 'numeric',
            hour: '2-digit', minute: '2-digit'
        });
    }

    get reportTitle() {
        return this.props.title || "Reporte Médico";
    }

    // ==================================================================
    // MÉTODO PRINCIPAL CON FALLBACK AUTOMÁTICO
    // ==================================================================
    async generatePDF(onlyBase64 = false) {
        // Intento 1: jsPDF puro (el más bonito y rápido)
        if (window.jspdf?.jsPDF) {
            try {
                const doc = await this._buildPDFWithJsPDF();
                return onlyBase64 ? doc.output("datauristring").split(",")[1] : doc;
            } catch (err) {
                console.warn("jsPDF puro falló, usando fallback html2canvas", err);
            }
        }

        // Intento 2: Fallback con html2canvas (siempre funciona)
        console.log("Generando PDF con fallback html2canvas + jsPDF");
        this.notification.add("Generando PDF (modo seguro)...", { type: "info" });

        const { jsPDF } = await this._loadJsPDFDynamic(); // carga jsPDF si no está
        const canvas = await this._renderReportToCanvas();
        const imgData = canvas.toDataURL("image/png");

        const doc = new jsPDF("p", "mm", "a4");
        const imgWidth = 210;
        const pageHeight = 295;
        const imgHeight = (canvas.height * imgWidth) / canvas.width;
        let heightLeft = imgHeight;

        let position = 0;
        doc.addImage(imgData, "PNG", 0, position, imgWidth, imgHeight);
        heightLeft -= pageHeight;

        while (heightLeft >= 0) {
            position = heightLeft - imgHeight;
            doc.addPage();
            doc.addImage(imgData, "PNG", 0, position, imgWidth, imgHeight);
            heightLeft -= pageHeight;
        }

        return onlyBase64 ? doc.output("datauristring").split(",")[1] : doc;
    }

    // ==================================================================
    // 1. Generación con jsPDF puro (el bueno)
    // ==================================================================
    async _buildPDFWithJsPDF() {
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF({ orientation: "portrait", unit: "mm", format: "a4" });

        const pageWidth = doc.internal.pageSize.getWidth();
        const pageHeight = doc.internal.pageSize.getHeight();
        const margin = 15;
        let y = margin;

        // Encabezado azul
        doc.setFillColor(41, 128, 185);
        doc.rect(0, 0, pageWidth, 30, "F");
        doc.setTextColor(255, 255, 255);
        doc.setFontSize(16);
        doc.setFont("helvetica", "bold");
        doc.text("CENTRO MÉDICO ESPECIALIZADO", pageWidth / 2, 15, { align: "center" });
        doc.setFontSize(11);
        doc.text("Acreditado - Excelencia en Salud", pageWidth / 2, 22, { align: "center" });

        // Logo
        if (this.state.companyLogo) {
            try {
                doc.addImage(`data:image/png;base64,${this.state.companyLogo}`, "PNG", 15, 8, 20, 20);
            } catch (e) { /* ignorar */ }
        }

        y = 40;
        doc.setTextColor(0, 0, 0);
        doc.setFontSize(18);
        doc.setFont("helvetica", "bold");
        doc.text(this.reportTitle.toUpperCase(), pageWidth / 2, y, { align: "center" });
        y += 15;

        doc.setDrawColor(41, 128, 185);
        doc.setLineWidth(0.5);
        doc.line(margin, y, pageWidth - margin, y);
        y += 15;

        // Contenido
        const text = this._extractCleanText();
        doc.setFontSize(11);
        doc.setTextColor(50, 50, 50);
        const lines = doc.splitTextToSize(text, pageWidth - margin * 2 - 10);
        lines.forEach(line => {
            if (y > pageHeight - 50) {
                doc.addPage();
                y = 30;
            }
            doc.text(line, margin + 5, y);
            y += 6;
        });

        // Firma y pie
        this._addSignatureAndFooter(doc, pageWidth, pageHeight);

        return doc;
    }

    // ==================================================================
    // 2. Fallback: renderizar el componente a canvas
    // ==================================================================
    async _renderReportToCanvas() {
        const html2canvas = window.html2canvas || (await this._loadHtml2Canvas());
        const element = this.__owl__.root.el.querySelector(".medical-report-container") || this.el;

        // Forzar estilos de impresión
        const originalDisplay = element.style.display;
        element.style.display = "block";

        const canvas = await html2canvas(element, {
            scale: 2,
            useCORS: true,
            backgroundColor: "#ffffff",
            logging: false,
        });

        element.style.display = originalDisplay;
        return canvas;
    }

    // ==================================================================
    // Carga dinámica de librerías (si no están ya)
    // ==================================================================
    async _loadJsPDFDynamic() {
        if (window.jspdf?.jsPDF) return window.jspdf;
        return new Promise((resolve) => {
            const script = document.createElement("script");
            script.src = "https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js";
            script.onload = () => resolve(window.jspdf);
            document.head.appendChild(script);
        });
    }

    async _loadHtml2Canvas() {
        return new Promise((resolve) => {
            const script = document.createElement("script");
            script.src = "https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js";
            script.onload = () => resolve(window.html2canvas);
            document.head.appendChild(script);
        });
    }

    // ==================================================================
    // Helpers
    // ==================================================================
    _extractCleanText() {
        const div = document.createElement("div");
        div.innerHTML = this.props.content || "";
        return (div.textContent || div.innerText || "").trim() || "Sin contenido.";
    }

    _addSignatureAndFooter(doc, pageWidth, pageHeight) {
        let y = doc.lastAutoTable ? doc.lastAutoTable.finalY + 30 : pageHeight - 70;

        doc.setDrawColor(100, 100, 100);
        doc.setLineWidth(0.3);
        doc.line(15, y, 75, y);
        doc.setFontSize(10);
        doc.setFont("helvetica", "bold");
        doc.text(this.state.userName, 15, y + 8);
        doc.setFont("helvetica", "normal");
        doc.text(this.state.userJobTitle, 15, y + 14);

        // Pie de página
        doc.setDrawColor(41, 128, 185);
        doc.line(15, pageHeight - 20, pageWidth - 15, pageHeight - 20);
        doc.setFontSize(8);
        doc.setTextColor(100, 100, 100);
        doc.text(`Reporte generado el ${this.currentDateTime} - Confidencial`, pageWidth / 2, pageHeight - 10, { align: "center" });
    }

    // ==================================================================
    // ACCIONES PÚBLICAS
    // ==================================================================
    downloadPDF = async () => {
        try {
            this.notification.add("Generando PDF...", { type: "info" });
            const doc = await this.generatePDF(false);
            const filename = `Reporte_Medico_${new Date().toISOString().slice(0,10).replace(/-/g,'')}_${Date.now()}.pdf`;
            doc.save(filename);
            this.notification.add("PDF descargado", { type: "success" });
        } catch (err) {
            this.notification.add("Error crítico generando PDF", { type: "danger" });
            console.error(err);
        }
    };

    sendEmail = async () => {
        if (!this.props.contacts?.length) {
            this.notification.add("Selecciona al menos un contacto", { type: "warning" });
            return;
        }

        try {
            this.notification.add("Preparando envío...", { type: "info" });
            const pdfBase64 = await this.generatePDF(true);

            const payload = {
                pdf_data: pdfBase64,
                pdf_name: `Reporte_Medico_${Date.now()}.pdf`,
                contacts: this.props.contacts,
                subject: `Reporte Médico - ${this.currentDate}`,
                body: `
Estimado/a paciente,

Adjuntamos su reporte médico generado el ${this.currentDateTime}.

Atentamente,
${this.state.userName}
${this.state.userJobTitle}
${this.state.companyName}

---
Mensaje automático.
                `.trim(),
                res_model: this.props.resModel || null,
                res_id: this.props.resId || null,
                timestamp: new Date().toISOString(),
                company_name: this.state.companyName,
                doctor_name: this.state.userName,
                doctor_title: this.state.userJobTitle,
            };

            const response = await fetch("/medical_report/send_to_n8n", {
                method: "POST",
                credentials: "include",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ params: payload }),
            });

            const result = await response.json();
            if (result.error) throw new Error(result.error);

            this.notification.add("Enviado correctamente", { type: "success" });
        } catch (err) {
            console.error(err);
            this.notification.add(`Error al enviar: ${err.message}`, { type: "danger" });
        }
    };

    printReport = () => window.print();
}