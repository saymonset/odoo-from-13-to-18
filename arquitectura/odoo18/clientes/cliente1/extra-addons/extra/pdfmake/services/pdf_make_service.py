# -*- coding: utf-8 -*-
import logging
import base64
from odoo import models, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class PdfMakeService(models.Model):
    _name = 'pdfmake.service'
    _description = 'Servicio PDFMake optimizado'

    @api.model
    def generate_medical_pdf(self, medical_data):
        """Genera PDF médico optimizado para evitar errores de memoria"""
        try:
            _logger.info("🎯 Iniciando generación de PDF optimizada")
            
            # ✅ 1. SIMPLIFICAR DATOS AL MÁXIMO
            simplified_data = self._prepare_simplified_data(medical_data)
            
            # ✅ 2. OPTIMIZAR LOGO (REDUCIR TAMAÑO)
            logo_str = self._get_optimized_logo()
            
            # ✅ 3. USAR TEMPLATE MÍNIMO
            html_content = self._render_minimal_html(simplified_data, logo_str)
            
            # ✅ 4. LIMPIAR HTML (CRÍTICO)
            html_content = self._clean_html(html_content)
            
            _logger.info(f"📊 HTML optimizado: {len(html_content)} caracteres")
            
            # ✅ 5. INTENTAR MÚLTIPLES MÉTODOS (con fallback)
            pdf_content = None
            
            # Método A: Usar _render_qweb_pdf si está disponible
            try:
                pdf_content = self._try_render_qweb_pdf(simplified_data, logo_str)
                if pdf_content:
                    _logger.info("✅ PDF generado con _render_qweb_pdf")
                    return pdf_content
            except Exception as e:
                _logger.warning(f"⚠️ _render_qweb_pdf falló: {e}")
            
            # Método B: Usar wkhtmltopdf con HTML optimizado
            try:
                pdf_content = self._try_wkhtmltopdf_safe(html_content)
                if pdf_content:
                    _logger.info("✅ PDF generado con wkhtmltopdf optimizado")
                    return pdf_content
            except Exception as e:
                _logger.warning(f"⚠️ wkhtmltopdf falló: {e}")
            
            # Método C: Último recurso - PDF básico sin imágenes
            if not pdf_content:
                pdf_content = self._generate_basic_pdf(simplified_data)
                if pdf_content:
                    _logger.info("✅ PDF generado básico (sin imágenes)")
                    return pdf_content
            
            # Si todo falla
            raise UserError(_(
                "No se pudo generar el PDF. "
                "Posibles causas:\n"
                "1. Memoria insuficiente en el servidor\n"
                "2. wkhtmltopdf necesita reinstalación\n"
                "3. Documento muy grande\n\n"
                "Contacte al administrador del sistema."
            ))
            
        except UserError:
            raise
        except Exception as e:
            _logger.error(f"❌ Error crítico: {str(e)}")
            raise UserError(_(
                f"Error al generar PDF: {str(e)[:100]}"
            ))

    def _prepare_simplified_data(self, medical_data):
        """Prepara datos mínimos necesarios"""
        from datetime import datetime
        
        return {
            'issue_date': medical_data.get('issue_date', datetime.now().strftime('%d/%m/%Y')),
            'patient_name': medical_data.get('patient_name', 'Paciente'),
            'doctor_name': medical_data.get('doctor_name', 'Dr. Médico'),
            'treatment': medical_data.get('treatment', ''),
            'recommendations': medical_data.get('recommendations', ''),
            'current_date': datetime.now().strftime('%d/%m/%Y'),
        }

    def _get_optimized_logo(self):
        """Obtiene y optimiza el logo para reducir memoria"""
        try:
            company = self.env.company
            if not company.logo:
                return ''
            
            # Si el logo es muy grande (> 50KB), usar versión reducida
            if len(company.logo) > 50000:
                _logger.warning("⚠️ Logo muy grande, usando versión minimal")
                # Convertir a string y truncar si es necesario
                if isinstance(company.logo, bytes):
                    logo_str = company.logo.decode('utf-8', errors='ignore')
                else:
                    logo_str = str(company.logo)
                
                # Limitar tamaño del logo
                if len(logo_str) > 5000:  # 5KB máximo
                    logo_str = logo_str[:5000]
                return logo_str
            else:
                # Logo pequeño, usar normalmente
                if isinstance(company.logo, bytes):
                    return company.logo.decode('utf-8', errors='ignore')
                return str(company.logo)
                
        except Exception as e:
            _logger.warning(f"⚠️ Error optimizando logo: {e}")
            return ''

    def _render_minimal_html(self, data, logo_str):
        """Renderiza HTML mínimo"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .content {{ margin: 20px 0; }}
                .footer {{ margin-top: 50px; text-align: center; }}
                .signature {{ margin-top: 100px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>Reporte Médico</h2>
                <p>Fecha: {data['current_date']}</p>
            </div>
            
            <div class="content">
                <p><strong>Paciente:</strong> {data['patient_name']}</p>
                <p><strong>Médico:</strong> {data['doctor_name']}</p>
                <p><strong>Tratamiento:</strong> {data.get('treatment', '')}</p>
                <p><strong>Recomendaciones:</strong></p>
                <p>{data.get('recommendations', '')}</p>
            </div>
            
            <div class="footer">
                <p>Documento generado el {data['current_date']}</p>
            </div>
        </body>
        </html>
        """

    def _clean_html(self, html_content):
        """Limpia HTML para reducir tamaño"""
        import re
        
        # Eliminar espacios múltiples
        html_content = re.sub(r'\s+', ' ', html_content)
        # Eliminar espacios entre tags
        html_content = re.sub(r'>\s+<', '><', html_content)
        # Eliminar comentarios
        html_content = re.sub(r'<!--.*?-->', '', html_content)
        
        return html_content.strip()

    def _try_render_qweb_pdf(self, data, logo_str):
        """Intenta usar el sistema de reportes de Odoo"""
        try:
            report = self.env['ir.actions.report'].sudo()
            
            # Buscar o crear un reporte temporal
            report_id = self.env.ref('pdfmake.medical_report_action', False)
            
            if report_id:
                pdf_content, _ = report._render_qweb_pdf(
                    report_id.report_name,
                    [],
                    data={'data': data, 'logo': logo_str}
                )
                return pdf_content
                
        except Exception as e:
            _logger.debug(f"Render qweb falló: {e}")
        
        return None

    def _try_wkhtmltopdf_safe(self, html_content):
        """Usa wkhtmltopdf con parámetros seguros"""
        try:
            # Dividir HTML si es muy grande
            if len(html_content) > 100000:  # 100KB
                html_content = html_content[:100000]
                _logger.warning("⚠️ HTML truncado a 100KB por seguridad")
            
            # Usar método interno con timeout
            IrReport = self.env['ir.actions.report'].sudo()
            
            # Llamar a _run_wkhtmltopdf directamente
            pdf_content = IrReport._run_wkhtmltopdf(
                [html_content],
                landscape=False
            )
            
            return pdf_content
            
        except MemoryError:
            _logger.error("💥 ERROR DE MEMORIA en wkhtmltopdf")
            raise
        except Exception as e:
            _logger.error(f"Error en wkhtmltopdf: {e}")
            return None

    def _generate_basic_pdf(self, data):
        """Genera PDF básico como último recurso"""
        from io import BytesIO
        try:
            # Usar reportlab para PDF simple (sin dependencias externas)
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.units import cm
            
            buffer = BytesIO()
            p = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4
            
            # Contenido básico
            p.setFont("Helvetica-Bold", 16)
            p.drawString(2*cm, height-3*cm, "Reporte Médico")
            
            p.setFont("Helvetica", 12)
            p.drawString(2*cm, height-4.5*cm, f"Paciente: {data['patient_name']}")
            p.drawString(2*cm, height-5.5*cm, f"Médico: {data['doctor_name']}")
            p.drawString(2*cm, height-6.5*cm, f"Fecha: {data['current_date']}")
            
            p.showPage()
            p.save()
            
            return buffer.getvalue()
            
        except ImportError:
            _logger.warning("ReportLab no está instalado")
            return None
        except Exception as e:
            _logger.error(f"Error con ReportLab: {e}")
            return None