/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

const { Component, xml } = owl;

class PdfmakeDownloadAction extends Component {
    setup() {
        this.notification = useService("notification");
        this.action = useService("action");
        
        // Ejecutar inmediatamente al cargar el componente
        this.generatePdf();
    }

    async generatePdf() {
        try {
            console.log("🔧 PdfmakeDownloadAction iniciado con params:", this.props.params);
            
            if (typeof pdfMake === 'undefined') {
                throw new Error("PDFMake no está disponible en el navegador");
            }

            // VALIDAR Y SANITIZAR PARÁMETROS
            const params = this.props.params || {};
            const name = params.name || 'Sin nombre';
            const amount = Number(params.amount) || 0;
            const active = params.active || false;
            const partner_name = params.partner_name || 'Ninguno';

            console.log("📊 Parámetros sanitizados:", { name, amount, active, partner_name });

            const docDefinition = {
                content: [
                    {text: 'REPORTE PDFMAKE DESDE ODOO', style: 'title'},
                    {text: '✅ ¡Generado correctamente!', style: 'subtitle'},
                    {text: '\n'},
                    {text: 'Datos del registro:', style: 'header'},
                    {
                        table: {
                            widths: ['*', '*'],
                            body: [
                                ['Campo', 'Valor'],
                                ['Nombre', name],
                                ['Importe', `€${amount.toFixed(2)}`],
                                ['Activo', active ? 'Sí' : 'No'],
                                ['Contacto', partner_name],
                            ]
                        }
                    },
                    {text: '\n'},
                    {text: `Generado el: ${new Date().toLocaleString('es-ES')}`, style: 'footer'},
                ],
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

            const fileName = `Reporte_${name.replace(/\s+/g, '_')}.pdf`;
            
            // Usar callback para saber cuando se completa la descarga
            pdfMake.createPdf(docDefinition).download(fileName, () => {
                console.log("✅ PDF descargado exitosamente:", fileName);
                
                this.notification.add(
                    `PDF generado: ${fileName}`,
                    { type: 'success' }
                );

                // Cerrar la acción después de descargar
                setTimeout(() => {
                    this.action.doAction({ type: 'ir.actions.act_window_close' });
                }, 1000);
            });
            
        } catch (error) {
            console.error('❌ Error en PdfmakeDownloadAction:', error);
            
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

// ✅ CORREGIDO: Usar xml tag para el template
PdfmakeDownloadAction.template = xml`
    <div class="text-center p-4">
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Generando PDF...</span>
        </div>
        <p class="mt-2">Generando PDF, por favor espere...</p>
    </div>
`;

registry.category("actions").add("pdfmake_download", PdfmakeDownloadAction);

console.log("✅ Acción pdfmake_download registrada correctamente");