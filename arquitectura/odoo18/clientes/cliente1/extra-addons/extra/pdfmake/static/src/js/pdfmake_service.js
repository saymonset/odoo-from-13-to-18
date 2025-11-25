/** @odoo-module **/

import { registry } from "@web/core/registry";

class PDFMakeService {
    constructor() {
        this._available = false;
        this._checkAvailability();
    }

    _checkAvailability() {
        if (typeof pdfMake !== 'undefined' && typeof pdfMake.createPdf === 'function') {
            this._available = true;
            console.log("✅ PDFMake Service: PDFMake detectado correctamente");
        } else {
            console.warn("❌ PDFMake Service: PDFMake no está disponible");
            // Intentar cargar PDFMake dinámicamente
            this._loadPDFMake();
        }
    }

    _loadPDFMake() {
        // Cargar PDFMake dinámicamente si no está disponible
        if (typeof pdfMake === 'undefined') {
            console.log("🔄 Intentando cargar PDFMake dinámicamente...");
            const script1 = document.createElement('script');
            script1.src = 'https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.2.10/pdfmake.min.js';
            script1.onload = () => {
                const script2 = document.createElement('script');
                script2.src = 'https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.2.10/vfs_fonts.js';
                script2.onload = () => {
                    this._available = true;
                    console.log("✅ PDFMake cargado dinámicamente");
                };
                document.head.appendChild(script2);
            };
            document.head.appendChild(script1);
        }
    }

    isAvailable() {
        return this._available;
    }

    /**
     * Genera y descarga un PDF
     */
    generatePDF(docDefinition, fileName = "document.pdf") {
        if (!this.isAvailable()) {
            throw new Error("PDFMake no está disponible en el navegador");
        }
        
        return new Promise((resolve, reject) => {
            try {
                console.log("📄 PDFMake Service: Generando PDF...");
                
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
     * Reporte Hola Mundo
     */
    createHelloWorldReport(data) {
        return {
            content: [
                { text: 'HOLA MUNDO', style: 'header' },
                { text: `Nombre: ${data.name}`, style: 'body' },
                { text: `ID Registro: ${data.record_id || 'N/A'}`, style: 'body' },
                { text: `Campo prueba: ${data.test_field || 'N/A'}`, style: 'body' },
                { text: `Generado: ${new Date().toLocaleString('es-ES')}`, style: 'footer' }
            ],
            styles: {
                'header': { fontSize: 22, bold: true, alignment: 'center', margin: [0, 60, 0, 20] },
                'body': { fontSize: 14, margin: [0, 0, 0, 10] },
                'footer': { fontSize: 10, italics: true, alignment: 'center', margin: [0, 0, 0, 20] }
            },
            pageMargins: [40, 60, 40, 60]
        };
    }

    /**
     * Constancia de Empleo (adaptado de NestJS)
     */
    createEmploymentLetterReport(data) {
        const styles = {
            header: {
                fontSize: 22,
                bold: true,
                alignment: 'center',
                margin: [0, 60, 0, 20],
            },
            body: {
                fontSize: 12,
                alignment: 'justify',
                lineHeight: 1.5,
                margin: [0, 0, 0, 15],
            },
            signature: {
                fontSize: 14,
                bold: true,
                margin: [0, 10, 0, 5],
            },
            footer: {
                fontSize: 10,
                italics: true,
                alignment: 'center',
                margin: [0, 0, 0, 20],
            },
        };

        const content = [
            {
                text: 'CONSTANCIA DE EMPLEO',
                style: 'header',
            },
            {
                text: [
                    `Yo, `,
                    { text: data.employer_name, bold: true },
                    `, en mi calidad de `,
                    { text: data.employer_position, bold: true },
                    ` de `,
                    { text: data.employer_company, bold: true },
                    `, por medio de la presente certifico que `,
                    { text: data.employee_name, bold: true },
                    ` ha sido empleado en nuestra empresa desde el `,
                    { text: data.employee_start_date, bold: true },
                    `.`
                ],
                style: 'body',
            },
            {
                text: `Durante su empleo, el Sr./Sra. ${data.employee_name} ha desempeñado el cargo de ${data.employee_position}, demostrando responsabilidad, compromiso y habilidades profesionales en sus labores.`,
                style: 'body',
            },
            {
                text: `La jornada laboral del Sr./Sra. ${data.employee_name} es de ${data.employee_hours} horas semanales, con un horario de ${data.employee_work_schedule}, cumpliendo con las políticas y procedimientos establecidos por la empresa.`,
                style: 'body',
            },
            {
                text: `Esta constancia se expide a solicitud del interesado para los fines que considere conveniente.`,
                style: 'body',
            },
            { text: `\n` },
            { text: `Atentamente,`, style: 'signature' },
            { text: data.employer_name, style: 'signature' },
            { text: data.employer_position, style: 'signature' },
            { text: data.employer_company, style: 'signature' },
            { text: `Fecha de emisión: ${data.issue_date}`, style: 'signature' },
        ];

        return {
            content: content,
            styles: styles,
            pageMargins: [40, 60, 40, 60],
            footer: {
                text: 'Este documento es una constancia de empleo y no representa un compromiso laboral.',
                style: 'footer',
            },
        };
    }

    /**
     * Método principal que decide qué reporte generar
     */
    generateReportByType(params) {
        console.log("📋 Generando reporte tipo:", params.report_type);
        
        switch (params.report_type) {
            case 'hello_world':
                return this.createHelloWorldReport(params);
            case 'employment_letter':
                return this.createEmploymentLetterReport(params);
            default:
                throw new Error(`Tipo de reporte no soportado: ${params.report_type}`);
        }
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