/** @odoo-module **/
import { Component } from "@odoo/owl";
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
    }

    get currentDate() {
        return new Date().toLocaleDateString('es-ES', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    get reportTitle() {
        return this.props.title || "Reporte Médico";
    }

    // 🔥 DESCARGA REAL DE PDF - CON MEJOR MANEJO DE ERRORES
    downloadPDF = async () => {
        try {
            this.notification.add("📄 Generando PDF...", { type: "info" });

            // Pequeña pausa para que el usuario vea el mensaje
            await new Promise(resolve => setTimeout(resolve, 500));

            // Verificar si jsPDF está disponible
            if (window.jspdf && typeof window.jspdf !== 'undefined') {
                console.log("📄 Usando jsPDF para generar PDF...");
                await this.generatePDFWithJSPDF();
            } else {
                console.log("📄 jsPDF no disponible, usando método simple...");
                await this.generateSimplePDF();
            }

            this.notification.add("✅ PDF descargado correctamente", { type: "success" });
        } catch (error) {
            console.error("❌ Error generando PDF:", error);
            this.notification.add("❌ Error al generar PDF: " + error.message, { type: "danger" });
        }
    }

    // 🔥 MÉTODO PRINCIPAL CON JSPDF
    generatePDFWithJSPDF = async () => {
        try {
            const { jsPDF } = window.jspdf;
            
            // Crear nuevo documento PDF
            const doc = new jsPDF();
            
            // Configuración del documento
            const pageWidth = doc.internal.pageSize.getWidth();
            const margin = 20;
            const contentWidth = pageWidth - (margin * 2);
            
            // 🔥 ENCABEZADO DEL REPORTE
            doc.setFontSize(20);
            doc.setFont("helvetica", "bold");
            doc.text(this.reportTitle, margin, margin + 10);
            
            // Información de la clínica
            doc.setFontSize(10);
            doc.setFont("helvetica", "normal");
            doc.text("CENTRO MÉDICO ESPECIALIZADO", pageWidth - margin - 60, margin + 5);
            doc.text("Tel: (123) 456-7890", pageWidth - margin - 60, margin + 10);
            doc.text("Email: info@centromedico.com", pageWidth - margin - 60, margin + 15);
            
            // Línea separadora
            doc.setDrawColor(200, 200, 200);
            doc.line(margin, margin + 20, pageWidth - margin, margin + 20);
            
            // 🔥 INFORMACIÓN DEL REPORTE
            let yPosition = margin + 35;
            
            doc.setFontSize(12);
            doc.setFont("helvetica", "bold");
            doc.text("INFORMACIÓN DEL REPORTE:", margin, yPosition);
            
            yPosition += 10;
            doc.setFont("helvetica", "normal");
            doc.text(`Fecha de emisión: ${this.currentDate}`, margin, yPosition);
            yPosition += 8;
            doc.text(`Médico responsable: Dr. Alejandro Rodríguez`, margin, yPosition);
            yPosition += 8;
            doc.text(`Especialidad: Medicina General`, margin, yPosition);
            
            // 🔥 CONTENIDO PRINCIPAL
            yPosition += 20;
            doc.setFont("helvetica", "bold");
            doc.text("INFORME MÉDICO:", margin, yPosition);
            
            yPosition += 10;
            doc.setFont("helvetica", "normal");
            doc.setFontSize(11);
            
            // 🔥 CORRECCIÓN: Obtener el contenido como texto plano
            const cleanContent = this.extractTextContent(this.props.content);
            
            // Dividir el texto en líneas
            const lines = doc.splitTextToSize(cleanContent, contentWidth);
            
            // Agregar cada línea al PDF
            lines.forEach(line => {
                if (yPosition > doc.internal.pageSize.getHeight() - margin - 20) {
                    doc.addPage();
                    yPosition = margin;
                }
                doc.text(line, margin, yPosition);
                yPosition += 7;
            });
            
            // 🔥 PIE DE PÁGINA Y FIRMA
            yPosition = doc.internal.pageSize.getHeight() - margin;
            doc.setFontSize(8);
            doc.setFont("helvetica", "italic");
            doc.text("Reporte generado automáticamente - Centro Médico Especializado", 
                    margin, yPosition);
            
            // FIRMA
            yPosition -= 20;
            doc.setFontSize(10);
            doc.setFont("helvetica", "bold");
            doc.text("_________________________", margin, yPosition);
            doc.text("Dr. Alejandro Rodríguez", margin, yPosition + 5);
            doc.text("Médico Especialista", margin, yPosition + 10);
            
            // 🔥 GUARDAR PDF
            const timestamp = new Date().getTime();
            doc.save(`reporte_medico_${timestamp}.pdf`);
            
        } catch (error) {
            console.error("❌ Error en generatePDFWithJSPDF:", error);
            throw new Error("No se pudo generar el PDF con jsPDF");
        }
    }

    // 🔥 MÉTODO SIMPLE (fallback)
    generateSimplePDF = () => {
        try {
            // 🔥 CORRECCIÓN: Usar extractTextContent en lugar de cleanHTMLContent
            const cleanContent = this.extractTextContent(this.props.content);
            
            const pdfContent = `
REPORTE MÉDICO
==============

Centro Médico Especializado
Fecha: ${this.currentDate}
Médico: Dr. Alejandro Rodríguez

INFORME:
${cleanContent}

Firma: _________________________
Dr. Alejandro Rodríguez
Médico Especialista

Reporte generado automáticamente
            `.trim();
            
            // Crear blob y descargar
            const blob = new Blob([pdfContent], { type: 'text/plain; charset=utf-8' });
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `reporte_medico_${new Date().getTime()}.txt`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
            
        } catch (error) {
            console.error("❌ Error en generateSimplePDF:", error);
            throw new Error("No se pudo generar el archivo de texto");
        }
    }

    // 🔥 NUEVO MÉTODO: Extraer texto de contenido HTML/string
    extractTextContent = (content) => {
        if (!content) return 'No hay contenido disponible';
        
        // Si es string con HTML, limpiarlo
        if (typeof content === 'string') {
            return content
                .replace(/<br\s*\/?>/gi, '\n')
                .replace(/<p>/gi, '\n')
                .replace(/<\/p>/gi, '\n')
                .replace(/<strong>(.*?)<\/strong>/gi, '$1')
                .replace(/<em>(.*?)<\/em>/gi, '$1')
                .replace(/<[^>]+>/g, '')
                .replace(/&nbsp;/g, ' ')
                .replace(/&amp;/g, '&')
                .replace(/&lt;/g, '<')
                .replace(/&gt;/g, '>')
                .replace(/\n\s*\n/g, '\n\n')
                .trim();
        }
        
        // Si es algún otro tipo, convertirlo a string
        return String(content);
    }

    // 🔥 ELIMINADO: cleanHTMLContent ya no se usa

    printReport = () => {
        window.print();
    }
}