/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

const { Component } = owl;

class GeneratePdfAction extends Component {
    setup() {
        this.notification = useService("notification");
        this.action = useService("action");
    }

    async willStart() {
        await this.generatePdf();
    }

    async generatePdf() {
        try {
            const params = this.props.params;
            
            if (typeof pdfMake === 'undefined') {
                throw new Error("PDFMake no está cargado en el navegador");
            }

            const docDefinition = {
                content: [
                    {text: 'REPORTE PDFMAKE DESDE ODOO', style: 'title'},
                    {text: '✅ ¡Generado desde la aplicación!', style: 'subtitle'},
                    {text: '\n'},
                    
                    {text: 'Datos del registro:', style: 'header'},
                    {
                        table: {
                            widths: ['*', '*'],
                            body: [
                                ['Campo', 'Valor'],
                                ['Nombre', params.name || 'No definido'],
                                ['Importe', `€${(params.amount || 0).toFixed(2)}`],
                                ['Activo', params.active ? 'Sí' : 'No'],
                                ['Contacto', params.partner_name || 'Ninguno'],
                                ['ID Registro', params.record_id?.toString() || 'N/A'],
                            ]
                        }
                    },
                    {text: '\n'},
                    {
                        table: {
                            headerRows: 1,
                            widths: ['*', 'auto', 'auto'],
                            body: [
                                [
                                    {text: 'Producto', style: 'tableHeader'},
                                    {text: 'Cantidad', style: 'tableHeader'}, 
                                    {text: 'Precio', style: 'tableHeader'}
                                ],
                                ['Impresora 3D Pro', 1, '€2.599,00'],
                                ['Filamento PLA 1kg', 3, '€74,97'],
                                ['Kit herramientas', 2, '€89,98'],
                                [
                                    {text: 'TOTAL', colSpan: 2, style: 'totalRow'}, 
                                    {}, 
                                    {text: '€2.763,95', style: 'totalRow'}
                                ],
                            ]
                        }
                    },
                    {text: '\n\n'},
                    {text: `Generado el: ${new Date().toLocaleString('es-ES')}`, style: 'footer'},
                ],
                styles: {
                    'title': {
                        fontSize: 22, 
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
                        margin: [0, 0, 0, 20]
                    },
                    'header': {
                        fontSize: 16, 
                        bold: true, 
                        margin: [0, 15, 0, 8]
                    },
                    'tableHeader': {
                        bold: true, 
                        fontSize: 12, 
                        color: 'white', 
                        fillColor: '#1976d2'
                    },
                    'totalRow': {
                        bold: true, 
                        fontSize: 13, 
                        color: 'white', 
                        fillColor: '#0d47a1'
                    },
                    'footer': {
                        fontSize: 10, 
                        italics: true, 
                        color: '#666666', 
                        alignment: 'center'
                    }
                },
                defaultStyle: {
                    font: 'Roboto'
                }
            };

            const fileName = `Reporte_${params.name}_${new Date().getTime()}.pdf`;
            pdfMake.createPdf(docDefinition).download(fileName);
            
            this.notification.add(
                `PDF generado correctamente: ${fileName}`,
                { type: 'success' }
            );

            setTimeout(() => {
                this.action.doAction({ type: 'ir.actions.act_window_close' });
            }, 1000);

        } catch (error) {
            console.error('Error generando PDF:', error);
            
            this.notification.add(
                `Error generando PDF: ${error.message}`,
                { type: 'danger' }
            );

            setTimeout(() => {
                this.action.doAction({ type: 'ir.actions.act_window_close' });
            }, 3000);
        }
    }
}

GeneratePdfAction.template = `
    <div class="text-center p-4">
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Generando PDF...</span>
        </div>
        <p class="mt-2">Generando PDF, por favor espere...</p>
    </div>
`;

registry.category("actions").add("generate_pdf_action", GeneratePdfAction);