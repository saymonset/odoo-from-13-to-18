/** @odoo-module **/

console.log("🔧 PDFMake Service: Iniciando carga...");

import { registry } from "@web/core/registry";

class PDFMakeService {
    constructor() {
        console.log("🔧 PDFMake Service: Constructor ejecutado");
        this._available = false;
        this._checkAvailability();
    }

    _checkAvailability() {
        if (typeof pdfMake !== 'undefined' && typeof pdfMake.createPdf === 'function') {
            this._available = true;
            console.log("✅ PDFMake Service: PDFMake detectado correctamente");
        } else {
            console.warn("❌ PDFMake Service: PDFMake no está disponible");
        }
    }

    isAvailable() {
        return this._available;
    }

    createPdf(docDefinition, fileName = "document.pdf") {
        if (!this.isAvailable()) {
            throw new Error("PDFMake no está disponible en el navegador");
        }
        
        return new Promise((resolve, reject) => {
            try {
                console.log("📄 PDFMake Service: Generando PDF...", docDefinition);
                pdfMake.createPdf(docDefinition).download(fileName, () => {
                    console.log("✅ PDFMake Service: PDF generado exitosamente");
                    resolve();
                });
            } catch (error) {
                console.error("❌ PDFMake Service: Error generando PDF", error);
                reject(error);
            }
        });
    }

    createTestDocument(recordData = {}) {
        return {
            content: [
                {text: 'REPORTE DE PRUEBA PDFMAKE', style: 'title'},
                {text: '✅ ¡Servicio funcionando correctamente!', style: 'subtitle'},
                {text: '\n'},
                {text: `Fecha: ${new Date().toLocaleString()}`},
                {text: '\n'},
                {
                    table: {
                        headerRows: 1,
                        widths: ['*', 'auto'],
                        body: [
                            [
                                {text: 'Campo', style: 'tableHeader'},
                                {text: 'Valor', style: 'tableHeader'}
                            ],
                            ['Nombre', recordData.name || 'Test'],
                            ['Importe', `€${(recordData.amount || 0).toFixed(2)}`],
                            ['Activo', recordData.active ? 'Sí' : 'No'],
                        ]
                    }
                },
            ],
            styles: {
                'title': {fontSize: 20, bold: true, color: '#1976d2', alignment: 'center', margin: [0, 0, 0, 10]},
                'subtitle': {fontSize: 14, italics: true, color: '#424242', alignment: 'center', margin: [0, 0, 0, 15]},
                'tableHeader': {bold: true, fontSize: 12, color: 'white', fillColor: '#1976d2'}
            }
        };
    }
}

// Crear instancia del servicio
const pdfMakeService = new PDFMakeService();

// Registrar el servicio
try {
    registry.category("services").add("pdfmake_service", {
        start() {
            console.log("🚀 PDFMake Service: Servicio registrado exitosamente");
            return pdfMakeService;
        }
    });
    console.log("✅ PDFMake Service: Registro completado");
} catch (error) {
    console.error("❌ PDFMake Service: Error registrando servicio", error);
}

// Exponer globalmente para pruebas
window.pdfmakeService = pdfMakeService;
console.log("🌐 PDFMake Service: Servicio expuesto globalmente como window.pdfmakeService");

export default pdfMakeService;