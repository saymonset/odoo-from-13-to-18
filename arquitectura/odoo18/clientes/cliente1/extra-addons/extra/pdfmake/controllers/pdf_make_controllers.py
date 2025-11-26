# controllers/pdfmake_controller.py
import json
import logging
import base64
from odoo import http
from odoo.http import request, Response
from datetime import datetime

_logger = logging.getLogger(__name__)

class PdfMakeController(http.Controller):
    
    # ENDPOINTS MÉDICOS CON QWEB
    @http.route('/pdfmake/medical-report-qweb', type='http', auth='user', methods=['GET'])
    def medical_report_qweb(self, **kw):
        """Endpoint principal para reportes médicos con QWeb"""
        try:
            _logger.info("🎯 Generando reporte médico con QWeb")
            
            # Recoger todos los parámetros
            medical_data = {
                'patient_name': kw.get('patient_name', 'Paciente'),
                'patient_age': kw.get('patient_age', ''),
                'patient_gender': kw.get('patient_gender', ''),
                'diagnosis': kw.get('diagnosis', 'Diagnóstico no especificado.'),
                'recommendations': kw.get('recommendations', 'Seguir controles médicos periódicos.'),
                'treatment': kw.get('treatment', ''),
                'doctor_name': kw.get('doctor_name', 'Dr. Médico'),
                'doctor_specialty': kw.get('doctor_specialty', 'Médico General'),
                'medical_center': kw.get('medical_center', 'Centro Médico'),
                'report_type': kw.get('report_type', 'basic'),
                'include_signature': kw.get('include_signature', 'True') == 'True',
                'issue_date': kw.get('issue_date', ''),
                'current_datetime': kw.get('current_datetime', ''),
            }
            
            # Determinar qué template usar según el tipo
            template_map = {
                'basic': 'pdfmake.medical_report_basic',
                'detailed': 'pdfmake.medical_report_detailed',
                'prescription': 'pdfmake.medical_prescription'
            }
            
            template = template_map.get(medical_data['report_type'], 'pdfmake.medical_report_basic')
            
            pdf = request.env['ir.actions.report'].sudo()._render_qweb_pdf(
                template,
                [],
                data={'medical_data': medical_data}
            )
            
            if pdf and len(pdf) == 1:
                filename = f"reporte_medico_{medical_data['patient_name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                
                return Response(
                    pdf[0],
                    headers=[
                        ('Content-Type', 'application/pdf'),
                        ('Content-Disposition', f'attachment; filename="{filename}"')
                    ]
                )
            else:
                raise Exception("No se pudo generar el PDF")
                
        except Exception as e:
            _logger.error(f"Error en medical_report_qweb: {str(e)}")
            return Response(
                f"Error generando PDF médico: {str(e)}",
                content_type='text/plain',
                status=500
            )

    @http.route('/pdfmake/medical-report/service', type='http', auth='user', methods=['POST'], csrf=False)
    def medical_report_service0(self, **post):
        """Endpoint HTTP para que Chatter Voice Note genere PDFs médicos"""
        try:
            import json
            
            # Obtener datos del body JSON
            raw_data = request.httprequest.data.decode('utf-8')
            json_data = json.loads(raw_data)
            medical_data = json_data.get('medical_data', {})
            
            _logger.info(f"Datos recibidos: {medical_data}")
            
            if not medical_data.get('diagnosis'):
                return json.dumps({'success': False, 'error': 'El diagnóstico es requerido'})
            
            # Usar el servicio PDFMake
            pdf_service = request.env['pdfmake.service'].sudo()
            pdf_content = pdf_service.generate_medical_pdf(medical_data)
            
            if pdf_content:
                # Convertir a base64 para fácil transporte
                pdf_b64 = base64.b64encode(pdf_content).decode('utf-8')
                
                response = {
                    'success': True,
                    'pdf_content': pdf_b64,
                    'filename': f"reporte_medico_{medical_data.get('patient_name', 'paciente').replace(' ', '_')}.pdf",
                    'message': 'PDF generado exitosamente por PDFMake'
                }
                return json.dumps(response)
            else:
                return json.dumps({'success': False, 'error': 'No se pudo generar el PDF'})
                
        except Exception as e:
            _logger.error(f"Error en servicio médico: {str(e)}")
            return json.dumps({'success': False, 'error': str(e)})
        
    @http.route('/pdfmake/audioreports', type='http', auth='public', csrf=False, methods=['GET', 'POST'])
    def audioReports(self, **kw):
        try:
            _logger.info("📥 Request recibido en /pdfmake/audioreports")
            
            prompt = kw.get('prompt') 
            if not prompt and request.httprequest.method == 'POST':
                try:
                    json_data = request.httprequest.get_json()
                    prompt = json_data.get('prompt') if json_data else None
                except:
                    pass
            
            _logger.info(f"🔍 Prompt recibido: {prompt}")
            
            if not prompt:
                return Response(
                    json.dumps({'error': 'No prompt provided'}),
                    content_type='application/json',
                    status=400
                )
            
            try:
                service = request.env['pdf_make.service'].sudo()
                result = service.pdfMake(prompt)
                _logger.info(f"✅ Resultado del servicio: {result}")
            except Exception as model_error:
                _logger.error(f"❌ Error accediendo al modelo: {model_error}")
                return Response(
                    json.dumps({'error': f'Model service error: {str(model_error)}'}),
                    content_type='application/json',
                    status=500
                )
            
            return Response(
                json.dumps(result),
                content_type='application/json',
                status=200
            )
            
        except Exception as e:
            _logger.error(f"💥 Error general en controlador: {str(e)}")
            return Response(
                json.dumps({'error': f'Internal server error: {str(e)}'}),
                content_type='application/json',
                status=500
            )

    # ENDPOINT HELLO WORLD - Genera PDF directamente
    @http.route('/pdfmake/hello', type='http', auth='user', methods=['GET'])
    def hello_report(self, **kw):
        """Endpoint para reporte Hola Mundo que devuelve PDF"""
        try:
            _logger.info("🎯 Generando reporte Hola Mundo via HTTP")
            
            # Crear PDF usando el reporte de Odoo
            pdf = self._generate_hello_world_pdf()
            
            # Devolver el PDF como respuesta
            return Response(
                pdf,
                headers=[
                    ('Content-Type', 'application/pdf'),
                    ('Content-Disposition', f'attachment; filename="hola_mundo_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"')
                ]
            )
            
        except Exception as e:
            _logger.error(f"Error en hello_report: {str(e)}")
            return Response(
                f"Error generando PDF: {str(e)}",
                content_type='text/plain',
                status=500
            )

    # ENDPOINT CONSTANCIA DE EMPLEO GENÉRICA
    @http.route('/pdfmake/employment-letter', type='http', auth='user', methods=['GET'])
    def employment_letter(self, **kw):
        """Endpoint para constancia de empleo genérica que devuelve PDF"""
        try:
            _logger.info("🎯 Generando constancia de empleo genérica via HTTP")
            
            # Datos por defecto
            default_data = {
                'employee_name': 'Juan Pérez',
                'employee_position': 'Desarrollador Senior',
                'employee_start_date': '15/03/2022',
                'employee_hours': 40,
                'employee_work_schedule': 'Lunes a Viernes 9:00-18:00',
                'employer_name': 'María García',
                'employer_position': 'Gerente de RRHH',
                'employer_company': 'Mi Empresa S.A.',
                'issue_date': datetime.now().strftime('%d/%m/%Y')
            }
            
            # Sobrescribir con parámetros de la URL si existen
            for key in default_data:
                if key in kw:
                    default_data[key] = kw[key]
            
            pdf = self._generate_employment_letter_pdf(default_data)
            
            return Response(
                pdf,
                headers=[
                    ('Content-Type', 'application/pdf'),
                    ('Content-Disposition', f'attachment; filename="constancia_empleo_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"')
                ]
            )
            
        except Exception as e:
            _logger.error(f"Error en employment_letter: {str(e)}")
            return Response(
                f"Error generando PDF: {str(e)}",
                content_type='text/plain',
                status=500
            )

    # ENDPOINT CONSTANCIA DE EMPLEO ESPECÍFICA
    @http.route('/pdfmake/employment-letter/<int:employee_id>', type='http', auth='user', methods=['GET'])
    def employment_letter_by_id(self, employee_id, **kw):
        """Endpoint para constancia de empleo específica que devuelve PDF"""
        try:
            _logger.info(f"🎯 Generando constancia de empleo para empleado ID: {employee_id}")
            
            # Buscar el empleado en Odoo
            employee = request.env['test.pdf.report'].sudo().browse(employee_id)
            if not employee.exists():
                return Response(
                    json.dumps({'error': 'Employee not found'}),
                    content_type='application/json',
                    status=404
                )
            
            # Preparar datos del empleado
            employee_data = {
                'employee_name': employee.name or "Empleado",
                'employee_position': employee.employee_position or "Empleado",
                'employee_start_date': employee.employee_start_date.strftime('%d/%m/%Y') if employee.employee_start_date else '01/01/2023',
                'employee_hours': employee.employee_hours_per_week or 40,
                'employee_work_schedule': employee.employee_work_schedule or 'Lunes a Viernes 9:00-18:00',
                'employer_name': employee.employer_name or 'Nombre del Empleador',
                'employer_position': employee.employer_position or 'Gerente de RRHH',
                'employer_company': employee.employer_company or 'Mi Empresa S.A.',
                'issue_date': datetime.now().strftime('%d/%m/%Y')
            }
            
            pdf = self._generate_employment_letter_pdf(employee_data)
            
            return Response(
                pdf,
                headers=[
                    ('Content-Type', 'application/pdf'),
                    ('Content-Disposition', f'attachment; filename="constancia_empleo_{employee.name.replace(" ", "_")}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"')
                ]
            )
            
        except Exception as e:
            _logger.error(f"Error en employment_letter_by_id: {str(e)}")
            return Response(
                f"Error generando PDF: {str(e)}",
                content_type='text/plain',
                status=500
            )

    # MÉTODOS PRIVADOS PARA GENERAR PDFs
    def _generate_hello_world_pdf(self):
        """Genera PDF de Hola Mundo usando el sistema de reportes de Odoo"""
        try:
            # Usar el reporte QWeb de Odoo
            pdf = request.env['ir.actions.report'].sudo()._render_qweb_pdf(
                'pdfmake.hello_world_report',
                [],  # No necesitamos registros específicos
                data={}
            )
            
            if pdf and len(pdf) == 1:
                return pdf[0]
            else:
                raise Exception("No se pudo generar el PDF")
                
        except Exception as e:
            _logger.error(f"Error generando PDF Hola Mundo: {str(e)}")
            # Fallback: crear un PDF simple con reportlab
            return self._create_simple_pdf("HOLA MUNDO", "Este es un reporte de prueba generado desde Odoo")

    def _generate_employment_letter_pdf(self, data):
        """Genera PDF de constancia de empleo - VERSIÓN DEFINITIVA"""
        try:
            _logger.info("🔄 Usando método directo para generar PDF")
            _logger.info("📋 Datos del empleado: %s", data)
            
            # Método DIRECTO: Renderizar template manualmente y convertir a PDF
            html_content = request.env['ir.ui.view']._render_template(
                'pdfmake.employment_letter_report',
                {'employee_data': data}  # Pasar los datos directamente al contexto
            )
            
            # Convertir HTML a PDF
            pdf = request.env['ir.actions.report']._run_wkhtmltopdf(
                [html_content],
                landscape=False,
                specific_paperformat_args={'data-report-margin-top': 10, 'data-report-margin-bottom': 10}
            )
            
            _logger.info("✅ PDF generado exitosamente con método directo")
            return pdf
                
        except Exception as e:
            _logger.error(f"❌ Error con método directo: {str(e)}")
            # Fallback robusto
            return self._create_employment_letter_fallback_pdf(data)

    def _create_employment_letter_fallback_pdf(self, data):
        """Fallback robusto para generar PDF"""
        try:
            _logger.info("🔄 Usando fallback para generar PDF")
            
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            from io import BytesIO
            
            buffer = BytesIO()
            pdf = canvas.Canvas(buffer, pagesize=A4)
            
            # Configurar el PDF
            pdf.setTitle("Constancia de Empleo")
            
            # Título
            pdf.setFont("Helvetica-Bold", 16)
            pdf.drawCentredString(300, 800, "CONSTANCIA DE EMPLEO")
            
            # Contenido
            pdf.setFont("Helvetica", 12)
            y_position = 750
            
            # Texto de la constancia
            texto = [
                f"Yo, {data.get('employer_name', 'Nombre del Empleador')}, en mi calidad de",
                f"{data.get('employer_position', 'Cargo del Empleador')} de {data.get('employer_company', 'Nombre de la Empresa')},",
                f"por medio de la presente certifico que {data.get('employee_name', 'Nombre del Empleado')}",
                f"ha sido empleado en nuestra empresa desde el {data.get('employee_start_date', 'Fecha de Inicio')}.",
                "",
                f"Durante su empleo, el Sr./Sra. {data.get('employee_name', 'Nombre del Empleado')} ha desempeñado",
                f"el cargo de {data.get('employee_position', 'Cargo del Empleado')}, demostrando responsabilidad,",
                "compromiso y habilidades profesionales en sus labores.",
                "",
                f"La jornada laboral del Sr./Sra. {data.get('employee_name', 'Nombre del Empleado')} es de",
                f"{data.get('employee_hours', 40)} horas semanales, con un horario de",
                f"{data.get('employee_work_schedule', 'Horario de Trabajo')}, cumpliendo con las políticas",
                "y procedimientos establecidos por la empresa.",
                "",
                "Esta constancia se expide a solicitud del interesado para los fines que",
                "considere conveniente.",
                "",
                "Atentamente,",
                "",
                data.get('employer_name', 'Nombre del Empleador'),
                data.get('employer_position', 'Cargo del Empleador'),
                data.get('employer_company', 'Nombre de la Empresa'),
                f"Fecha de emisión: {data.get('issue_date', 'Fecha')}"
            ]
            
            # Escribir cada línea
            for line in texto:
                if y_position < 50:  # Nueva página si se acaba el espacio
                    pdf.showPage()
                    pdf.setFont("Helvetica", 12)
                    y_position = 800
                
                pdf.drawString(50, y_position, line)
                y_position -= 20
            
            # Footer
            pdf.setFont("Helvetica-Oblique", 8)
            pdf.drawCentredString(300, 30, 
                "Este documento es una constancia de empleo y no representa un compromiso laboral.")
            
            pdf.save()
            buffer.seek(0)
            _logger.info("✅ PDF de fallback generado exitosamente")
            return buffer.getvalue()
            
        except Exception as e:
            _logger.error(f"❌ Error en fallback PDF: {str(e)}")
            # Último recurso: PDF MUY simple
            return self._create_simple_pdf(
                "CONSTANCIA DE EMPLEO", 
                f"""
                Empleado: {data.get('employee_name', 'N/A')}
                Cargo: {data.get('employee_position', 'N/A')}
                Empresa: {data.get('employer_company', 'N/A')}
                Fecha Inicio: {data.get('employee_start_date', 'N/A')}
                Horas: {data.get('employee_hours', 'N/A')}
                Horario: {data.get('employee_work_schedule', 'N/A')}
                """
            )

    def _create_simple_pdf(self, title, content):
        """Crea un PDF simple como fallback usando reportlab"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            from io import BytesIO
            
            buffer = BytesIO()
            pdf = canvas.Canvas(buffer, pagesize=letter)
            
            # Configurar el PDF
            pdf.setTitle(title)
            pdf.setFont("Helvetica-Bold", 16)
            pdf.drawString(100, 750, title)
            
            pdf.setFont("Helvetica", 12)
            y_position = 700
            for line in content.split('\n'):
                if y_position < 50:  # Nueva página si se acaba el espacio
                    pdf.showPage()
                    pdf.setFont("Helvetica", 12)
                    y_position = 750
                
                pdf.drawString(50, y_position, line.strip())
                y_position -= 20
            
            pdf.save()
            buffer.seek(0)
            return buffer.getvalue()
            
        except ImportError:
            _logger.error("ReportLab no está disponible")
            # Último fallback: devolver texto plano
            return f"{title}\n\n{content}".encode('utf-8')