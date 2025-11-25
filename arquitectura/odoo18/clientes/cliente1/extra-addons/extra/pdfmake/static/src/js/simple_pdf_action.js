/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

const { Component, xml, onWillStart, onMounted } = owl;

class PdfmakeDownloadAction extends Component {
    setup() {
        this.notification = useService("notification");
        this.action = useService("action");
        this.pdfMakeService = useService("pdfmake_service");
        
        console.log("🔍 DIAGNÓSTICO - Props recibidos:", this.props);
        console.log("🔍 DIAGNÓSTICO - Parámetros:", this.props.params);
        console.log("🔍 DIAGNÓSTICO - Contexto:", this.props.context);
        console.log("🔍 DIAGNÓSTICO - Action:", this.props.action);
        
        onMounted(async () => {
            await this.generateReport();
        });
    }

    async generateReport() {
        try {
            console.log("🎯 Iniciando generación de reporte...");
            
            // Obtener parámetros de diferentes fuentes posibles
            const params = this.getActionParams();
            console.log("📦 Parámetros finales:", params);

            if (!params.report_type) {
                console.error("❌ No se encontró report_type en:", params);
                throw new Error("No se especificó el tipo de reporte");
            }

            // Generar la definición del documento según el tipo
            const docDefinition = this.pdfMakeService.generateReportByType(params);
            
            // Crear nombre de archivo
            const fileName = this.generateFileName(params);
            
            // Generar y descargar PDF
            await this.pdfMakeService.generatePDF(docDefinition, fileName);
            
            this.notification.add(
                `PDF generado exitosamente: ${fileName}`, 
                { type: 'success' }
            );
            
            // Cerrar la ventana después de un breve delay
            setTimeout(() => {
                this.action.doAction({ type: 'ir.actions.act_window_close' });
            }, 2000);
            
        } catch (error) {
            console.error('❌ Error generando reporte:', error);
            this.notification.add(
                `Error generando PDF: ${error.message}`, 
                { type: 'danger' }
            );
            
            setTimeout(() => {
                this.action.doAction({ type: 'ir.actions.act_window_close' });
            }, 3000);
        }
    }

    getActionParams() {
        // Intentar obtener parámetros de diferentes fuentes
        if (this.props.params && Object.keys(this.props.params).length > 0) {
            return this.props.params;
        }
        
        if (this.props.context && this.props.context.params) {
            return this.props.context.params;
        }
        
        if (this.props.action && this.props.action.params) {
            return this.props.action.params;
        }
        
        // Si no hay parámetros, devolver objeto vacío
        return {};
    }

    generateFileName(params) {
        const timestamp = new Date().toISOString().slice(0, 10);
        
        switch (params.report_type) {
            case 'hello_world':
                return `Hola_Mundo_${params.name || 'test'}_${timestamp}.pdf`;
            case 'employment_letter':
                return `Constancia_Empleo_${params.employee_name || 'empleado'}_${timestamp}.pdf`;
            default:
                return `documento_${timestamp}.pdf`;
        }
    }
}

PdfmakeDownloadAction.template = xml`
    <div class="text-center p-4">
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Generando PDF...</span>
        </div>
        <p class="mt-2">Generando documento PDF...</p>
        <p class="text-muted small">Espere un momento por favor</p>
    </div>
`;

PdfmakeDownloadAction.props = {
    params: { type: Object, optional: true },
    context: { type: Object, optional: true },
    action: { type: Object, optional: true },
};

registry.category("actions").add("pdfmake_download", PdfmakeDownloadAction);