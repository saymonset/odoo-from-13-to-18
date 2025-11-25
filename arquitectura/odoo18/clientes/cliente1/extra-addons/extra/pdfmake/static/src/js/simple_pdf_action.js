/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

const { Component, xml, onWillStart } = owl;

class PdfmakeDownloadAction extends Component {
    setup() {
        this.notification = useService("notification");
        this.action = useService("action");
        
        onWillStart(async () => {
            await this.diagnoseAndGenerate();
        });
    }

    async diagnoseAndGenerate() {
        console.group("🔍 DIAGNÓSTICO COMPLETO PDFMAKE");
        
        // Diagnosticar todas las posibles fuentes de parámetros
        console.log("1. this.props:", this.props);
        console.log("2. this.props.params:", this.props.params);
        console.log("3. this.props.action:", this.props.action);
        console.log("4. this.props.action?.params:", this.props.action?.params);
        console.log("5. this.props.action?.context:", this.props.action?.context);
        
        // Probar diferentes formas de acceder a los parámetros
        const sources = {
            'direct_params': this.props.params,
            'action_params': this.props.action?.params,
            'action_context': this.props.action?.context,
            'window_params': window.pdfmakeParams // Por si acaso
        };
        
        console.log("6. Todas las fuentes posibles:", sources);
        
        // Intentar encontrar los parámetros en cualquier lugar
        let finalParams = {};
        
        for (const [sourceName, source] of Object.entries(sources)) {
            if (source && typeof source === 'object' && Object.keys(source).length > 0) {
                console.log(`✅ Parámetros encontrados en: ${sourceName}`, source);
                finalParams = source;
                break;
            }
        }
        
        console.log("7. Parámetros finales a usar:", finalParams);
        console.groupEnd();
        
        if (Object.keys(finalParams).length === 0) {
            console.error("❌ No se encontraron parámetros en ninguna fuente");
            this.notification.add(
                "Error: No se recibieron datos para el PDF",
                { type: 'danger', sticky: true }
            );
            setTimeout(() => {
                this.action.doAction({ type: 'ir.actions.act_window_close' });
            }, 3000);
            return;
        }
        
        await this.generatePdf(finalParams);
    }

    async generatePdf(params) {
        try {
            console.log("🎯 Generando PDF con parámetros:", params);
            
            // Extraer valores
            const name = String(params.name || 'Sin nombre').trim();
            const amount = parseFloat(params.amount) || 0;
            const active = Boolean(params.active);
            const partner_name = String(params.partner_name || 'Ninguno').trim();
            const record_id = params.record_id || null;

            console.log("📊 Valores extraídos:", { name, amount, active, partner_name, record_id });

            if (typeof pdfMake === 'undefined') {
                throw new Error("PDFMake no está disponible");
            }

            const docDefinition = {
                content: [
                    {text: 'REPORTE PDFMAKE - DIAGNÓSTICO', style: 'title'},
                    {text: 'Parámetros recibidos:', style: 'header'},
                    {
                        table: {
                            widths: ['40%', '60%'],
                            body: [
                                ['Fuente', 'Valor'],
                                ['Nombre', name],
                                ['Importe', `€${amount.toFixed(2)}`],
                                ['Activo', active ? 'Sí' : 'No'],
                                ['Contacto', partner_name],
                                ['ID', record_id || 'N/A'],
                            ]
                        }
                    },
                    {text: `Generado: ${new Date().toLocaleString('es-ES')}`, style: 'footer'},
                ],
                styles: {
                    'title': { fontSize: 16, bold: true, alignment: 'center', margin: [0, 0, 0, 10] },
                    'header': { fontSize: 14, bold: true, margin: [0, 10, 0, 5] },
                    'footer': { fontSize: 10, color: '#666666', alignment: 'center' }
                }
            };

            const fileName = `Diagnostico_${name}_${Date.now()}.pdf`;
            pdfMake.createPdf(docDefinition).download(fileName);
            
            this.notification.add(`PDF generado: ${fileName}`, { type: 'success' });
            
            setTimeout(() => {
                this.action.doAction({ type: 'ir.actions.act_window_close' });
            }, 1500);
            
        } catch (error) {
            console.error('❌ Error:', error);
            this.notification.add(`Error: ${error.message}`, { type: 'danger' });
            setTimeout(() => {
                this.action.doAction({ type: 'ir.actions.act_window_close' });
            }, 3000);
        }
    }
}

PdfmakeDownloadAction.template = xml`
    <div class="text-center p-4">
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Diagnosticando...</span>
        </div>
        <p class="mt-2">Analizando parámetros y generando PDF...</p>
        <p class="text-muted small">Revise la consola para ver el diagnóstico</p>
    </div>
`;

PdfmakeDownloadAction.props = {
    params: { type: Object, optional: true },
};

registry.category("actions").add("pdfmake_download", PdfmakeDownloadAction);