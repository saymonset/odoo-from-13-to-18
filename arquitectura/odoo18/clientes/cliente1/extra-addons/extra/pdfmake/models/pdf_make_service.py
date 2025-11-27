# -*- coding: utf-8 -*-
import logging
from odoo import models, api
from odoo.http import request
import base64  # Solo si necesitas conversión manual

_logger = logging.getLogger(__name__)

class PdfMakeService(models.Model):
    _name = 'pdfmake.service'
    _description = 'Servicio PDFMake para generación de PDFs'

    @api.model
    def generate_medical_pdf(self, medical_data):
        """Genera PDF médico con logo DEBUG en Odoo 18"""
        try:
            _logger.info("🔍 [DEBUG] Iniciando generación PDF médico")

            # Compañía actual
            company = self.env.company
            _logger.info(f"🏢 [DEBUG] Compañía: {company.name} (ID: {company.id})")

            # MÉTODO 1: report_header_logo (oficial para PDFs)
            logo_str = company.report_header_logo
            _logger.info(f"📷 [DEBUG] report_header_logo existe: {'SÍ' if logo_str else 'NO'}")
            if logo_str:
                _logger.info(f"📏 [DEBUG] Longitud report_header_logo: {len(logo_str)} caracteres (debe ser >1000)")

            # FALLBACK: Si no hay report_header_logo, usa image_1920 (el campo de imagen principal)
            if not logo_str:
                if company.image_1920:
                    # image_1920 es bytes, convertir a base64 string
                    logo_str = base64.b64encode(company.image_1920).decode('utf-8')
                    _logger.info(f"✅ [DEBUG] Usando fallback image_1920: {len(logo_str)} caracteres")
                else:
                    _logger.warning("⚠️ [DEBUG] NI report_header_logo NI image_1920 disponibles")

            # Si aún no hay logo, usa un placeholder base64 (para testing)
            if not logo_str:
                # Logo de prueba: un cuadrado rojo simple (base64 mini)
                placeholder_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
                logo_str = placeholder_b64
                _logger.info("🆘 [DEBUG] Usando logo placeholder (cuadrado rojo para testing)")

            _logger.info(f"🎯 [DEBUG] Logo final disponible: {'SÍ' if logo_str else 'NO'} (long: {len(logo_str)})")

            # Valores por defecto
            from datetime import datetime
            medical_data.setdefault('issue_date', datetime.now().strftime('%d/%m/%Y'))
            medical_data.setdefault('current_datetime', datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
            medical_data.setdefault('patient_name', 'Paciente')
            medical_data.setdefault('doctor_name', 'Dr. Médico')
            medical_data.setdefault('medical_center', company.name or 'Centro Médico')
            medical_data.setdefault('doctor_specialty', 'Médico General')
            medical_data.setdefault('patient_age', '')
            medical_data.setdefault('patient_gender', '')
            medical_data.setdefault('treatment', '')
            medical_data.setdefault('recommendations', 'Seguir controles médicos periódicos.')
            medical_data.setdefault('include_signature', True)

            template_map = {
                'basic': 'pdfmake.medical_report_basic',
                'detailed': 'pdfmake.medical_report_detailed',
            }
            template_name = template_map.get(medical_data.get('report_type', 'basic'), 'pdfmake.medical_report_basic')
            _logger.info(f"📄 [DEBUG] Template: {template_name}")

            context = {
                'medical_data': medical_data,
                'company': company,
                'logo_str': logo_str,  # ¡Aquí va el logo listo!
                'datetime': datetime,
            }

            # Renderizar (asegúrate de que tu template use este contexto)
            html_content = request.env['ir.ui.view'].sudo()._render_template(template_name, context)
            _logger.info(f"🌐 [DEBUG] HTML generado: {len(html_content)} caracteres")

            if not html_content:
                raise ValueError("Template vacío")

            # Generar PDF
            pdf_content = request.env['ir.actions.report'].sudo()._run_wkhtmltopdf([html_content])
            _logger.info(f"📄 [DEBUG] PDF generado: {len(pdf_content) if pdf_content else 0} bytes")

            if not pdf_content:
                raise ValueError("wkhtmltopdf falló")

            _logger.info("✅ PDF listo con logo!")
            return pdf_content

        except Exception as e:
            _logger.error("❌ Error PDF: %s", str(e), exc_info=True)
            return None