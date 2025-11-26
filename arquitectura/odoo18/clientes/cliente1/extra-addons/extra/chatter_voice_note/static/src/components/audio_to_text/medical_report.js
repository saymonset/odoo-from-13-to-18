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
        
        // SOLUCIÓN: Usar el servicio HTTP en lugar de RPC
        this.http = useService("http");
        
       
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
    // CARGA DE DATOS (Mantener igual)
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
    // UTILIDADES (Mantener igual)
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
    // SOLUCIÓN: Método mejorado para generar PDF
    // ==================================================================

downloadPDF = async () => {
    try {
        debugger;
        this.notification.add("Generando PDF...", { type: "info" });

        // Preparar datos médicos
        const medicalData = await this.prepareMedicalDataForPDFMake();
          
        // DEBUG: Verificar datos antes de enviar (usando console.log directamente)
        console.log("=== DATOS MÉDICOS PARA PDF ===");
        console.log("Diagnóstico:", medicalData.diagnosis);
        console.log("Tipo de diagnóstico:", typeof medicalData.diagnosis);
        console.log("Datos completos:", medicalData);
        
        // Verificar específicamente el diagnóstico
        if (!medicalData.diagnosis || medicalData.diagnosis.trim() === '') {
            throw new Error("El diagnóstico está vacío");
        }

        let result;

        // PRIMERO: Usar HTTP endpoint
        try {
            console.log("1. Intentando endpoint HTTP...");
            result = await this.generatePDFWithHTTP(medicalData);
            console.log("✅ HTTP exitoso:", result);
        } catch (httpError) {
            console.warn("HTTP falló:", httpError);
            
            // SEGUNDO: Intentar con QWEB endpoint
            try {
                console.log("2. Intentando endpoint QWEB...");
                result = await this.generatePDFWithHTTP(medicalData);
                console.log("✅ QWEB exitoso");
            } catch (qwebError) {
                console.warn("QWEB falló:", qwebError);
                
                // TERCERO: Fallback a jsPDF
                try {
                    console.log("3. Usando fallback jsPDF...");
                    result = await this.generatePDFFallback(medicalData);
                    console.log("✅ jsPDF exitoso");
                } catch (fallbackError) {
                    console.warn("jsPDF falló:", fallbackError);
                    throw new Error("Todos los métodos de generación fallaron");
                }
            }
        }

        if (result.success) {
            this.downloadPDFFile(result.pdf_content, result.filename);
            this.notification.add("PDF descargado exitosamente", { type: "success" });
        } else {
            throw new Error(result.error || "Error desconocido generando PDF");
        }

    } catch (err) {
        console.error("Error generando PDF:", err);
        this.notification.add(`Error generando PDF: ${err.message}`, { type: "danger" });
    }
};
    // ==================================================================
    // MÉTODOS MEJORADOS PARA GENERAR PDF
    // ==================================================================

   
  // MÉTODO PRINCIPAL RECOMENDADO - ORM
async generatePDFWithORM(medicalData) {
    try {
        debugger
        console.log("Generando PDF via ORM (método recomendado):", medicalData);
        
        const result = await this.orm.call(
            "pdfmake.service",           // Modelo
            "generate_medical_pdf",      // Método (según tu controlador)
            [medicalData],               // Parámetros como lista
            {}                           // Opciones adicionales
        );

        console.log("✅ ORM call exitoso:", result);
        return result;
        
    } catch (error) {
        console.error('Error en generatePDFWithORM:', error);
        throw error;
    }
}

// MÉTODO SIMPLIFICADO - Usa JSON simple
async generatePDFWithHTTP(medicalData) {
    try {
        console.log("Enviando datos al endpoint JSON:", medicalData);
        
        // Enviar JSON simple como Postman
        const response = await fetch('/pdfmake/medical-report/service', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                medical_data: medicalData
            }),
            credentials: 'include'
        });

        console.log("Estado de respuesta:", response.status, response.statusText);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        console.log("Respuesta completa:", result);
        
        return result;
        
    } catch (error) {
        console.error('Error en generatePDFWithHTTP:', error);
        throw error;
    }
}
// Método alternativo usando endpoint QWEB (sin validación estricta)
async generatePDFWithQWEB(medicalData) {
    try {
        // Convertir datos a parámetros URL
        const params = new URLSearchParams();
        
        // Asegurarse de que todos los valores sean strings
        Object.keys(medicalData).forEach(key => {
            let value = medicalData[key];
            if (value === null || value === undefined) {
                value = '';
            } else if (typeof value === 'boolean') {
                value = value.toString();
            }
            params.append(key, String(value));
        });

        const url = `/pdfmake/medical-report-qweb?${params.toString()}`;
        console.log("URL QWEB:", url);

        const response = await fetch(url, {
            method: 'GET',
            credentials: 'same-origin',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // Obtener el PDF como blob y convertirlo a base64
        const pdfBlob = await response.blob();
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => {
                const base64 = reader.result.split(',')[1];
                resolve({
                    success: true,
                    pdf_content: base64,
                    filename: `reporte_medico_${medicalData.patient_name || 'paciente'}.pdf`
                });
            };
            reader.onerror = () => reject(new Error('Error leyendo el blob del PDF'));
            reader.readAsDataURL(pdfBlob);
        });
        
    } catch (error) {
        console.error('Error en generatePDFWithQWEB:', error);
        throw error;
    }
}
    // Método 3: Fallback con jsPDF
    async generatePDFFallback(medicalData) {
        if (window.jspdf?.jsPDF) {
            const doc = await this._buildPDFWithJsPDF();
            const pdfOutput = doc.output('datauristring').split(',')[1]; // Extraer base64
            return {
                success: true,
                pdf_content: pdfOutput,
                filename: `Reporte_Medico_${new Date().toISOString().slice(0,10)}.pdf`
            };
        } else {
            throw new Error("No hay método de generación de PDF disponible");
        }
    }

    // ==================================================================
    // MANTENER LOS MÉTODOS EXISTENTES (con pequeñas mejoras)
    // ==================================================================

async prepareMedicalDataForPDFMake() {
    const extractedData = this.extractMedicalDataFromContent();
    
    // FUNCIÓN PARA CONVERTIR OBJETO A STRING
    const convertToString = (data) => {
        if (typeof data === 'string') return data;
        if (typeof data === 'object' && data !== null) {
            // Si es un objeto con claves numéricas (como {0: 'H', 1: 'o', ...})
            if (Object.keys(data).every(key => !isNaN(key))) {
                return Object.values(data).join('');
            }
            // Si es un objeto normal, convertirlo a JSON string
            return JSON.stringify(data);
        }
        return String(data || '');
    };

    // Convertir todos los campos que puedan ser objetos a strings
    const diagnosis = convertToString(extractedData.diagnosis || this.props.content || 'Diagnóstico no especificado.');
    const originalContent = convertToString(this.props.content);
    
    const medicalData = {
        patient_name: convertToString(extractedData.patientName || 'Paciente'),
        patient_age: convertToString(extractedData.patientAge || ''),
        patient_gender: convertToString(extractedData.patientGender || ''),
        diagnosis: diagnosis,
        recommendations: convertToString(extractedData.recommendations || 'Seguir controles médicos periódicos.'),
        treatment: convertToString(extractedData.treatment || ''),
        doctor_name: convertToString(this.state.userName),
        doctor_specialty: convertToString(this.state.userJobTitle),
        medical_center: convertToString(this.state.companyName),
        report_type: 'detailed',
        include_signature: true,
        issue_date: this.currentDate,
        current_datetime: this.currentDateTime,
        original_content: originalContent,
        source_module: 'chatter_voice_note',
        res_model: this.props.resModel,
        res_id: this.props.resId
    };

    // VERIFICACIÓN FINAL: Asegurar que diagnosis sea string no vacío
    if (!medicalData.diagnosis || medicalData.diagnosis.trim() === '') {
        medicalData.diagnosis = 'Diagnóstico no especificado.';
    }

    return medicalData;
} 
extractMedicalDataFromContent() {
    // Convertir content a string primero
    const convertToString = (data) => {
        if (typeof data === 'string') return data;
        if (typeof data === 'object' && data !== null) {
            if (Object.keys(data).every(key => !isNaN(key))) {
                return Object.values(data).join('');
            }
            return JSON.stringify(data);
        }
        return String(data || '');
    };

    const content = convertToString(this.props.content || '');
    const extracted = {
        patientName: '',
        patientAge: '',
        patientGender: '',
        diagnosis: '',
        recommendations: '',
        treatment: ''
    };

    try {
        const patterns = {
            patientName: /(paciente|sr|sra|srta)[:\s]*([^\n,.]+)/i,
            patientAge: /(\d+)\s*años|edad[:\s]*(\d+)/i,
            patientGender: /(masculino|femenino|hombre|mujer)/i,
            diagnosis: /(diagnóstico|dx|impresión)[:\s]*([^]+?)(?=tratamiento|recomendaciones|$)/i,
            treatment: /(tratamiento|rx|medicación)[:\s]*([^]+?)(?=recomendaciones|$)/i,
            recommendations: /(recomendaciones|indicaciones)[:\s]*([^]+?)$/i
        };

        const nameMatch = content.match(patterns.patientName);
        if (nameMatch) {
            extracted.patientName = nameMatch[2]?.trim() || nameMatch[1]?.trim();
        }

        const ageMatch = content.match(patterns.patientAge);
        if (ageMatch) {
            extracted.patientAge = ageMatch[1] || ageMatch[2];
        }

        const genderMatch = content.match(patterns.patientGender);
        if (genderMatch) {
            extracted.patientGender = this.formatGender(genderMatch[1]);
        }

        // Si no encontramos diagnóstico específico, usar todo el contenido
        if (!extracted.diagnosis) {
            extracted.diagnosis = content;
        }

    } catch (error) {
        console.warn("Error extrayendo datos médicos:", error);
        extracted.diagnosis = content;
    }

    return extracted;
}
    formatGender(gender) {
        const genderMap = {
            'masculino': 'Masculino',
            'hombre': 'Masculino', 
            'femenino': 'Femenino',
            'mujer': 'Femenino'
        };
        return genderMap[gender.toLowerCase()] || gender;
    }

    downloadPDFFile(pdfBase64, filename = null) {
        try {
            const byteCharacters = atob(pdfBase64);
            const byteNumbers = new Array(byteCharacters.length);
            
            for (let i = 0; i < byteCharacters.length; i++) {
                byteNumbers[i] = byteCharacters.charCodeAt(i);
            }
            
            const byteArray = new Uint8Array(byteNumbers);
            const blob = new Blob([byteArray], { type: 'application/pdf' });

            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            
            const finalFilename = filename || 
                `Reporte_Medico_${this.state.userName.replace('Dr. ', '').replace(/ /g, '_')}_${new Date().toISOString().slice(0,10)}.pdf`;
            
            link.download = finalFilename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);

        } catch (error) {
            console.error("Error descargando PDF:", error);
            throw new Error("Error al descargar el archivo PDF");
        }
    }

    // ==================================================================
    // MÉTODOS ORIGINALES (mantener para compatibilidad)
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
    // MÉTODOS DE EMAIL E IMPRESIÓN (mantener igual)
    // ==================================================================

    sendEmail = async () => {
        if (!this.props.contacts?.length) {
            this.notification.add("Selecciona al menos un contacto", { type: "warning" });
            return;
        }

        try {
            this.notification.add("Preparando envío...", { type: "info" });
            
            const medicalData = await this.prepareMedicalDataForPDFMake();
            const result = await this.generatePDFWithORM(medicalData); // Usar ORM para email

            if (!result.success) {
                throw new Error(result.error || "Error generando PDF para email");
            }

            const payload = {
                pdf_data: result.pdf_content,
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

            const response = await this.http.post("/medical_report/send_to_n8n", {
                params: payload
            });

            const emailResult = response;
            if (emailResult.error) throw new Error(emailResult.error);

            this.notification.add("Enviado correctamente", { type: "success" });
        } catch (err) {
            console.error(err);
            this.notification.add(`Error al enviar: ${err.message}`, { type: "danger" });
        }
    };

    printReport = () => window.print();
}