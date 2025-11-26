# -*- coding: utf-8 -*-
import logging
from odoo import models, api
from odoo.http import request

_logger = logging.getLogger(__name__)

class PdfMakeService(models.Model):
    _name = 'pdfmake.service'
    _description = 'Servicio PDFMake para generación de PDFs'

    @api.model
    def generate_medical_pdf(self, medical_data):
        """Genera PDF médico usando _render_template directamente"""
        try:
            _logger.info("🎯 Generando PDF médico usando método directo")
            
            # Agregar datos esenciales con valores por defecto
            from datetime import datetime
            medical_data.setdefault('issue_date', datetime.now().strftime('%d/%m/%Y'))
            medical_data.setdefault('current_datetime', datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
            medical_data.setdefault('patient_name', 'Paciente')
            medical_data.setdefault('doctor_name', 'Dr. Médico')
            medical_data.setdefault('medical_center', 'Centro Médico')
            medical_data.setdefault('doctor_specialty', 'Médico General')
            medical_data.setdefault('patient_age', '')
            medical_data.setdefault('patient_gender', '')
            medical_data.setdefault('treatment', '')
            medical_data.setdefault('recommendations', 'Seguir controles médicos periódicos.')
            medical_data.setdefault('include_signature', True)
            
            _logger.info(f"📋 Datos médicos para el PDF: {medical_data}")
            
            # Determinar template
            template_map = {
                'basic': 'pdfmake.medical_report_basic',
                'detailed': 'pdfmake.medical_report_detailed',
            }
            
            template_name = template_map.get(medical_data.get('report_type', 'basic'), 'pdfmake.medical_report_basic')
            _logger.info(f"🔄 Usando template: {template_name}")
            
            # 1. Primero renderizar el template a HTML
            html_content = request.env['ir.ui.view'].sudo()._render_template(
                template_name,
                {'medical_data': medical_data}
            )
            
            if not html_content:
                _logger.error("❌ El HTML está vacío después de renderizar el template")
                raise Exception("No se pudo renderizar el template HTML")
            
            _logger.info(f"✅ HTML renderizado - Tamaño: {len(html_content)} caracteres")
            
            # 2. Convertir HTML a PDF
            pdf_content = request.env['ir.actions.report'].sudo()._run_wkhtmltopdf(
                [html_content]
            )
            
            if pdf_content:
                _logger.info(f"✅ PDF generado exitosamente - Tamaño: {len(pdf_content)} bytes")
                return pdf_content
            else:
                _logger.error("❌ El PDF está vacío después de la conversión")
                raise Exception("No se pudo convertir HTML a PDF")
                
        except Exception as e:
            _logger.error(f"❌ Error generando PDF médico: {str(e)}")
            import traceback
            _logger.error(traceback.format_exc())
            return None