/** @odoo-module **/

import { registry } from "@web/core/registry";

class PDFMakeService {
    constructor() {
        this._available = false;
        this._checkAvailability();
    }

    // En tu PDFMakeService existente, agrega:

/**
 * Método de diagnóstico mejorado
 */
diagnoseParameters(params) {
    console.group("🔍 DIAGNÓSTICO PDFMAKE SERVICE");
    console.log("📦 Parámetros recibidos:", params);
    console.log("🔍 Tipo:", typeof params);
    console.log("📊 Es array?", Array.isArray(params));
    console.log("🗝️ Keys:", params ? Object.keys(params) : 'N/A');
    console.log("🔎 Valores:", params ? Object.values(params) : 'N/A');
    console.log("🌐 PDFMake disponible:", this.isAvailable());
    console.log("⏰ Timestamp:", new Date().toISOString());
    console.groupEnd();
    
    return {
        params_received: params,
        params_type: typeof params,
        is_array: Array.isArray(params),
        keys: params ? Object.keys(params) : [],
        values: params ? Object.values(params) : [],
        pdfmake_available: this.isAvailable(),
        timestamp: new Date().toISOString()
    };
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

    /**
     * Genera y descarga un PDF
     * @param {Object} docDefinition - Definición del documento para pdfMake
     * @param {String} fileName - Nombre del archivo
     * @returns {Promise}
     */
    
    generatePDF(docDefinition, fileName = "document.pdf") {
    if (!this.isAvailable()) {
        throw new Error("PDFMake no está disponible en el navegador");
    }
    
    return new Promise((resolve, reject) => {
        try {
            console.log("📄 PDFMake Service: Generando PDF...");
            console.log("📋 DocDefinition:", docDefinition);
            
            pdfMake.createPdf(docDefinition).download(fileName, () => {
                console.log("✅ PDFMake Service: PDF generado exitosamente");
                resolve(fileName);
            });
        } catch (error) {
            console.error("❌ PDFMake Service: Error generando PDF", error);
            reject(error);
        }
    });
}

    /**
     * Plantilla básica para reportes
     * @param {Object} data - Datos para el reporte
     * @returns {Object} docDefinition para pdfMake
     */
    createBasicReport(data) {
        const {
            title = "REPORTE PDFMAKE",
            subtitle = "Generado desde Odoo",
            fields = [],
            showTimestamp = true
        } = data;

        const tableBody = [['Campo', 'Valor']];
        
        fields.forEach(field => {
            tableBody.push([
                field.label || field.name,
                field.value !== undefined ? field.value : 'No disponible'
            ]);
        });

        const content = [
            { text: title, style: 'title' },
            { text: subtitle, style: 'subtitle' },
            { text: '\n' },
            { text: 'Datos del registro:', style: 'header' },
            {
                table: {
                    widths: ['*', '*'],
                    body: tableBody
                }
            }
        ];

        if (showTimestamp) {
            content.push(
                { text: '\n' },
                { text: `Generado el: ${new Date().toLocaleString('es-ES')}`, style: 'footer' }
            );
        }

        return {
            content,
            styles: {
                'title': {
                    fontSize: 18,
                    bold: true,
                    color: '#1976d2',
                    alignment: 'center',
                    margin: [0, 0, 0, 10]
                },
                'subtitle': {
                    fontSize: 14,
                    italics: true,
                    color: '#424242',
                    alignment: 'center',
                    margin: [0, 0, 0, 15]
                },
                'header': {
                    fontSize: 16,
                    bold: true,
                    margin: [0, 15, 0, 8]
                },
                'footer': {
                    fontSize: 10,
                    color: '#666666',
                    alignment: 'center'
                }
            }
        };
    }

    /**
     * Crea definición para test.pdf.report
     * @param {Object} recordData - Datos del registro
     * @returns {Object} docDefinition
     */
    createTestReportDefinition(recordData) {
        const fields = [
            { name: 'name', label: 'Nombre', value: recordData.name },
            { name: 'amount', label: 'Importe', value: `€${Number(recordData.amount || 0).toFixed(2)}` },
            { name: 'active', label: 'Activo', value: recordData.active ? 'Sí' : 'No' },
            { name: 'partner_name', label: 'Contacto', value: recordData.partner_name || 'Ninguno' }
        ];

        return this.createBasicReport({
            title: 'REPORTE PDFMAKE DESDE ODOO',
            subtitle: '✅ ¡Generado correctamente!',
            fields: fields,
            showTimestamp: true
        });
    }
}



// Crear instancia del servicio
const pdfMakeService = new PDFMakeService();

// Registrar el servicio
registry.category("services").add("pdfmake_service", {
    start() {
        console.log("🚀 PDFMake Service: Servicio registrado exitosamente");
        return pdfMakeService;
    }
});

export default pdfMakeService;