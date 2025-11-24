/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

const { Component, useState, onWillStart } = owl;

class TestPdfReport extends Component {
    setup() {
        this.pdfmakeService = useService("pdfmake_service");
        this.notification = useService("notification");
        this.action = useService("action");
        
        this.state = useState({
            loading: false,
            pdfmakeAvailable: false
        });
        
        onWillStart(async () => {
            this.state.pdfmakeAvailable = this.pdfmakeService.isAvailable();
        });
    }
    
    async generateTestPdf() {
        if (!this.state.pdfmakeAvailable) {
            this.notification.add(
                "PDFMake no está disponible en el navegador",
                { type: 'danger' }
            );
            return;
        }
        
        this.state.loading = true;
        
        try {
            // Datos del registro actual
            const recordData = {
                name: this.props.record.data.name,
                amount: this.props.record.data.amount,
                active: this.props.record.data.active,
                partner_name: this.props.record.data.partner_id ? this.props.record.data.partner_id[1] : 'Ninguno'
            };
            
            const docDefinition = this.pdfmakeService.createTestDocument(recordData);
            const fileName = `Test_PDF_${new Date().getTime()}.pdf`;
            
            await this.pdfmakeService.createPdf(docDefinition, fileName);
            
            this.notification.add(
                "PDF generado correctamente",
                { type: 'success' }
            );
            
        } catch (error) {
            console.error("Error generando PDF:", error);
            this.notification.add(
                `Error generando PDF: ${error.message}`,
                { type: 'danger' }
            );
        } finally {
            this.state.loading = false;
        }
    }
}

TestPdfReport.template = "pdfmake.TestPdfReport";
TestPdfReport.components = {};

// Registrar el componente en el formulario
registry.category("view_widgets").add("test_pdf_report_button", TestPdfReport);