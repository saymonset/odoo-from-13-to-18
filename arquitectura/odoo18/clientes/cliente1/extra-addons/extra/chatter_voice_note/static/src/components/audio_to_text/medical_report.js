/** @odoo-module **/
import { Component, useState } from "@odoo/owl"; 
import { useService } from "@web/core/utils/hooks";

export class MedicalReport extends Component {
    static template = "chatter_voice_note.MedicalReport";
    static props = {
        content: String,
        title: { type: String, optional: true },
        onClose: { type: Function, optional: true }
    };

    setup() {
        super.setup();
        this.notification = useService("notification");
        this.orm = useService("orm");

         this.state = useState({
                    companyLogo: null,
                    companyName: ''
                });

         this.loadCompanyLogo();        

    }

    // 🔥 MÉTODO PARA CARGAR EL LOGO DE LA COMPAÑÍA
async loadCompanyLogo() {
    try {
        console.log("🔄 Cargando logo de la compañía...");
        
        // Obtener información de la compañía actual
        const companies = await this.orm.searchRead(
            "res.company",
            [],
            ["logo", "name"],
            { limit: 1 }
        );
        
        if (companies.length > 0) {
            const company = companies[0];
            
            if (company.logo) {
                console.log("✅ Logo de compañía encontrado");
                this.state.companyLogo = company.logo;
            }
            
            if (company.name) {
                this.state.companyName = company.name;
            }
            
            console.log("🏢 Compañía:", company.name);
        } else {
            console.warn("⚠️ No se encontró información de la compañía");
        }
    } catch (error) {
        console.error("❌ Error cargando logo de compañía:", error);
    }
}

    get currentDate() {
        return new Date().toLocaleDateString('es-ES', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    get currentDateTime() {
        return new Date().toLocaleString('es-ES', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    get reportTitle() {
        return this.props.title || "Reporte Médico";
    }

    // 🔥 MÉTODO PARA OBTENER EL LOGO DE LA COMPAÑÍA
    async getCompanyLogo() {
        try {
            debugger
            const companies = await this.orm.searchRead(
                "res.company",
                [],
                ["logo"],
                { limit: 1 }
            );
            if (companies.length > 0 && companies[0].logo) {
                return companies[0].logo;
            }
        } catch (error) {
            console.error("Error al obtener el logo de la compañía:", error);
        }
        return null;
    }

    // 🔥 MÉTODO PARA CARGAR IMAGEN DESDE BASE64
    loadImageFromBase64(base64Data) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = function() {
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                canvas.width = img.width;
                canvas.height = img.height;
                ctx.drawImage(img, 0, 0);
                resolve(canvas.toDataURL('image/png'));
            };
            img.onerror = reject;
            img.src = `data:image/png;base64,${base64Data}`;
        });
    }

    // 🔥 DESCARGA REAL DE PDF PROFESIONAL
    downloadPDF = async () => {
        try {
            this.notification.add("📄 Generando PDF profesional...", { type: "info" });

            // Pequeña pausa para que el usuario vea el mensaje
            await new Promise(resolve => setTimeout(resolve, 500));

            // Verificar si jsPDF está disponible
            if (window.jspdf && typeof window.jspdf !== 'undefined') {
                console.log("📄 Usando jsPDF para generar PDF profesional...");
                await this.generateProfessionalPDF();
            } else {
                console.log("📄 jsPDF no disponible, usando método alternativo...");
                await this.generateAlternativePDF();
            }

            this.notification.add("✅ PDF profesional descargado correctamente", { type: "success" });
        } catch (error) {
            console.error("❌ Error generando PDF:", error);
            this.notification.add("❌ Error al generar PDF: " + error.message, { type: "danger" });
        }
    }

    // 🔥 PDF PROFESIONAL CON DISEÑO MÉDICO Y LOGO REAL
    generateProfessionalPDF = async () => {
        try {
            const { jsPDF } = window.jspdf;
            
            // Crear nuevo documento PDF en formato A4
            const doc = new jsPDF({
                orientation: 'portrait',
                unit: 'mm',
                format: 'a4'
            });
            
            const pageWidth = doc.internal.pageSize.getWidth();
            const pageHeight = doc.internal.pageSize.getHeight();
            const margin = 15;
            const contentWidth = pageWidth - (margin * 2);
            let yPosition = margin;

            // 🔥 ENCABEZADO PROFESIONAL CON FONDO
            doc.setFillColor(41, 128, 185); // Azul médico
            doc.rect(0, 0, pageWidth, 25, 'F');
            
            // Título principal en blanco
            doc.setFontSize(16);
            doc.setFont("helvetica", "bold");
            doc.setTextColor(255, 255, 255);
            doc.text("CENTRO MÉDICO ESPECIALIZADO", pageWidth / 2, 12, { align: "center" });
            
            doc.setFontSize(12);
            doc.text("Acreditado - Excelencia en Salud", pageWidth / 2, 18, { align: "center" });

            // 🔥 LOGO REAL DE LA COMPAÑÍA DE ODOO
            let logoLoaded = false;
            try {
                const companyLogo = await this.getCompanyLogo();
                if (companyLogo) {
                    const logoData = await this.loadImageFromBase64(companyLogo);
                    // Añadir el logo con dimensiones apropiadas
                    doc.addImage(logoData, 'PNG', 20, 8, 15, 15);
                    logoLoaded = true;
                    console.log("✅ Logo de la compañía cargado correctamente");
                }
            } catch (error) {
                console.warn("❌ No se pudo cargar el logo de la compañía:", error);
            }

            // 🔥 LOGO ALTERNATIVO SI NO SE PUDO CARGAR EL LOGO DE LA COMPAÑÍA
            if (!logoLoaded) {
                console.log("⚠️ Usando logo alternativo");
                doc.setFillColor(255, 255, 255);
                doc.circle(25, 12, 8, 'F');
                doc.setFontSize(10);
                doc.setTextColor(41, 128, 185);
                doc.text("CM", 25, 14, { align: "center" });
            }

            yPosition = 35;

            // 🔥 INFORMACIÓN DEL REPORTE
            doc.setFontSize(14);
            doc.setFont("helvetica", "bold");
            doc.setTextColor(0, 0, 0);
            doc.text(this.reportTitle.toUpperCase(), pageWidth / 2, yPosition, { align: "center" });
            
            yPosition += 10;

            // Línea decorativa
            doc.setDrawColor(41, 128, 185);
            doc.setLineWidth(0.5);
            doc.line(margin, yPosition, pageWidth - margin, yPosition);
            
            yPosition += 15;

            // 🔥 DATOS DEL PACIENTE (simulados - en producción vendrían de la base de datos)
            doc.setFontSize(10);
            doc.setFont("helvetica", "bold");
            doc.text("INFORMACIÓN DEL PACIENTE:", margin, yPosition);
            
            yPosition += 6;
            doc.setFont("helvetica", "normal");
            
            const patientData = [
                { label: "Nombre del Paciente:", value: "Juan Pérez García" },
                { label: "Edad:", value: "45 años" },
                { label: "Historial Clínico:", value: "HC-2024-001234" },
                { label: "Fecha de Consulta:", value: this.currentDate },
                { label: "Médico Tratante:", value: "Dr. Alejandro Rodríguez" },
                { label: "Especialidad:", value: "Medicina General" }
            ];

            patientData.forEach((data, index) => {
                if (index % 2 === 0 && index > 0) {
                    yPosition += 6;
                }
                
                const xPos = index % 2 === 0 ? margin : pageWidth / 2 + 5;
                
                doc.setFont("helvetica", "bold");
                doc.text(data.label, xPos, yPosition);
                doc.setFont("helvetica", "normal");
                doc.text(data.value, xPos + (index % 2 === 0 ? 45 : 40), yPosition);
                
                if (index % 2 !== 0) {
                    yPosition += 6;
                }
            });

            yPosition += 12;

            // 🔥 CONTENIDO PRINCIPAL DEL REPORTE
            doc.setFillColor(245, 245, 245);
            doc.roundedRect(margin, yPosition, contentWidth, 10, 2, 2, 'F');
            
            doc.setFontSize(11);
            doc.setFont("helvetica", "bold");
            doc.setTextColor(0, 0, 0);
            doc.text("INFORME MÉDICO DETALLADO", margin + 5, yPosition + 6);
            
            yPosition += 15;

            // Procesar el contenido
            const cleanContent = this.extractTextContent(this.props.content);
            
            // Configurar estilo para el contenido
            doc.setFontSize(10);
            doc.setFont("helvetica", "normal");
            doc.setTextColor(60, 60, 60);

            // Dividir el texto en líneas
            const lines = doc.splitTextToSize(cleanContent, contentWidth - 10);
            
            // Agregar cada línea al PDF con sangría
            lines.forEach(line => {
                if (yPosition > pageHeight - margin - 40) {
                    this.addNewPageWithHeader(doc, pageWidth);
                    yPosition = margin + 25;
                }
                doc.text("  " + line, margin + 5, yPosition);
                yPosition += 5;
            });

            yPosition += 10;

            // 🔥 FIRMA Y SELLO PROFESIONAL
            if (yPosition > pageHeight - margin - 50) {
                this.addNewPageWithHeader(doc, pageWidth);
                yPosition = margin + 25;
            }

            // Línea de firma
            doc.setDrawColor(150, 150, 150);
            doc.setLineWidth(0.3);
            doc.line(margin, yPosition, margin + 60, yPosition);
            
            doc.setFontSize(9);
            doc.setFont("helvetica", "bold");
            doc.text("Firma del Médico", margin, yPosition + 5);
            
            // Información del médico
            doc.setFont("helvetica", "normal");
            doc.text("Dr. Alejandro Rodríguez", margin, yPosition + 10);
            doc.text("Médico Especialista", margin, yPosition + 15);
            doc.text("Lic. MED-123456", margin, yPosition + 20);

            // Sello simulado
            doc.setDrawColor(200, 0, 0);
            doc.setLineWidth(0.5);
            doc.circle(pageWidth - margin - 30, yPosition + 10, 15, 'S');
            doc.setFontSize(6);
            doc.setTextColor(200, 0, 0);
            doc.text("SELLO OFICIAL", pageWidth - margin - 30, yPosition + 10, { align: "center" });
            doc.text("CENTRO MÉDICO", pageWidth - margin - 30, yPosition + 13, { align: "center" });

            yPosition += 35;

            // 🔥 PIE DE PÁGINA PROFESIONAL
            doc.setDrawColor(41, 128, 185);
            doc.setLineWidth(0.5);
            doc.line(margin, yPosition, pageWidth - margin, yPosition);
            
            yPosition += 5;
            
            doc.setFontSize(7);
            doc.setFont("helvetica", "italic");
            doc.setTextColor(100, 100, 100);
            doc.text(`Reporte generado automáticamente el ${this.currentDateTime} - Centro Médico Especializado - Tel: (123) 456-7890 - www.centromedico.com`, 
                    pageWidth / 2, yPosition, { align: "center" });
            
            doc.text(`Página 1 de 1 - Documento confidencial - No copiar ni distribuir sin autorización`, 
                    pageWidth / 2, yPosition + 4, { align: "center" });

            // 🔥 GUARDAR PDF CON NOMBRE PROFESIONAL
            const timestamp = new Date().toISOString().slice(0, 10).replace(/-/g, '');
            const fileName = `Reporte_Medico_${timestamp}_${new Date().getTime()}.pdf`;
            doc.save(fileName);
            
        } catch (error) {
            console.error("❌ Error en generateProfessionalPDF:", error);
            throw new Error("No se pudo generar el PDF profesional");
        }
    }

    // 🔥 MÉTODO PARA AÑADIR NUEVA PÁGINA CON ENCABEZADO
    addNewPageWithHeader(doc, pageWidth) {
        doc.addPage();
        
        // Encabezado en páginas siguientes
        doc.setFillColor(41, 128, 185);
        doc.rect(0, 0, pageWidth, 15, 'F');
        
        doc.setFontSize(10);
        doc.setFont("helvetica", "bold");
        doc.setTextColor(255, 255, 255);
        doc.text("CENTRO MÉDICO ESPECIALIZADO - CONTINUACIÓN DEL REPORTE", pageWidth / 2, 8, { align: "center" });
        
        return 25; // Retorna la posición Y inicial
    }

    // 🔥 MÉTODO ALTERNATIVO PARA PDF (cuando jsPDF no está disponible)
    generateAlternativePDF = () => {
        try {
            const cleanContent = this.extractTextContent(this.props.content);
            
            // Crear contenido HTML profesional para PDF
            const htmlContent = `
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>${this.reportTitle}</title>
    <style>
        @page {
            size: A4;
            margin: 20mm;
            @top-left {
                content: "CENTRO MÉDICO ESPECIALIZADO";
                font-size: 10pt;
                color: #2980b9;
            }
            @bottom-center {
                content: "Página " counter(page) " de " counter(pages);
                font-size: 8pt;
                color: #666;
            }
        }
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
        }
        .header {
            text-align: center;
            border-bottom: 3px solid #2980b9;
            padding-bottom: 15px;
            margin-bottom: 20px;
        }
        .title {
            font-size: 18pt;
            font-weight: bold;
            color: #2980b9;
            margin-bottom: 10px;
        }
        .patient-info {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 15px;
            margin: 20px 0;
        }
        .content {
            margin: 25px 0;
            white-space: pre-line;
            font-size: 11pt;
        }
        .signature {
            margin-top: 50px;
            border-top: 1px solid #ccc;
            padding-top: 20px;
        }
        .footer {
            font-size: 8pt;
            color: #666;
            text-align: center;
            margin-top: 30px;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="title">${this.reportTitle}</div>
        <div><strong>Centro Médico Especializado</strong></div>
        <div>Fecha de emisión: ${this.currentDateTime}</div>
    </div>
    
    <div class="patient-info">
        <strong>INFORMACIÓN DEL PACIENTE:</strong><br>
        Nombre: Juan Pérez García | Edad: 45 años<br>
        Historial Clínico: HC-2024-001234 | Médico: Dr. Alejandro Rodríguez
    </div>
    
    <div class="content">
        <strong>INFORME MÉDICO:</strong><br><br>
        ${cleanContent.replace(/\n/g, '<br>')}
    </div>
    
    <div class="signature">
        <div>_________________________</div>
        <div><strong>Dr. Alejandro Rodríguez</strong></div>
        <div>Médico Especialista - Lic. MED-123456</div>
    </div>
    
    <div class="footer">
        Reporte generado automáticamente - Centro Médico Especializado<br>
        Documento confidencial - No copiar ni distribuir sin autorización
    </div>
</body>
</html>
            `;
            
            // Crear blob como PDF (aunque será HTML, muchos navegadores lo abren como PDF)
            const blob = new Blob([htmlContent], { type: 'text/html' });
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `reporte_medico_${new Date().getTime()}.html`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
            
        } catch (error) {
            console.error("❌ Error en generateAlternativePDF:", error);
            throw new Error("No se pudo generar el archivo alternativo");
        }
    }

    // 🔥 EXTRAER TEXTO DEL CONTENIDO
    extractTextContent = (content) => {
        if (!content) return 'No hay contenido disponible para el reporte médico.';
        
        if (typeof content === 'string') {
            return content
                .replace(/<br\s*\/?>/gi, '\n')
                .replace(/<p>/gi, '\n')
                .replace(/<\/p>/gi, '\n')
                .replace(/<strong>(.*?)<\/strong>/gi, '**$1**')
                .replace(/<em>(.*?)<\/em>/gi, '*$1*')
                .replace(/<[^>]+>/g, '')
                .replace(/&nbsp;/g, ' ')
                .replace(/&amp;/g, '&')
                .replace(/&lt;/g, '<')
                .replace(/&gt;/g, '>')
                .replace(/\n\s*\n/g, '\n\n')
                .trim();
        }
        
        return String(content);
    }

    // 🔥 IMPRESIÓN MEJORADA
    printReport = () => {
        // Forzar los estilos de impresión
        const printStyles = `
            <style>
                ${document.querySelector('style[data-print]')?.innerHTML || ''}
                @media print {
                    body * { visibility: hidden; }
                    .medical-report-container, 
                    .medical-report-container * { 
                        visibility: visible; 
                    }
                    .medical-report-container {
                        position: absolute !important;
                        top: 0 !important;
                        left: 0 !important;
                        width: 100% !important;
                        background: white !important;
                    }
                }
            </style>
        `;
        
        // Agregar estilos temporalmente
        const styleElement = document.createElement('style');
        styleElement.innerHTML = printStyles;
        document.head.appendChild(styleElement);
        
        // Imprimir
        window.print();
        
        // Remover estilos después de imprimir
        setTimeout(() => {
            document.head.removeChild(styleElement);
        }, 1000);
    }
}