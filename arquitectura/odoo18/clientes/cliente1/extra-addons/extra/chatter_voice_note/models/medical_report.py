from odoo import models, fields, api
import base64
import logging

_logger = logging.getLogger(__name__)

class MailMail(models.Model):
    _inherit = 'mail.mail'

    @api.model
    def create_and_send_medical_report(self, email_data):
        _logger.info("🔄 Iniciando envío de reporte médico")
        try:
            # =======================
            # Extracción de datos
            # =======================
            pdf_data = email_data.get('pdf_data')
            pdf_name = email_data.get('pdf_name', 'reporte_medico.pdf')
            contacts = email_data.get('contacts', [])
            subject = email_data.get('subject', 'Reporte Médico')
            body = email_data.get('body', '')

            _logger.info(f"Datos recibidos: pdf_name={pdf_name}, contactos={contacts}, subject={subject}")

            if not pdf_data:
                _logger.error("❌ No se recibió PDF")
                return {'error': 'PDF no proporcionado'}

            if not contacts:
                _logger.error("❌ No se proporcionaron contactos")
                return {'error': 'No hay destinatarios'}

            # =======================
            # Preparar destinatarios
            # =======================
            partner_ids = []
            for contact in contacts:
                partner_id = contact.get('id')
                if partner_id:
                    partner_ids.append(partner_id)
                    _logger.info(f"✅ Agregado destinatario: {contact.get('name')} (ID: {partner_id})")

            if not partner_ids:
                _logger.error("❌ Ningún contacto tiene ID válido")
                return {'error': 'No hay destinatarios válidos'}

            # =======================
            # Decodificar PDF
            # =======================
            try:
                pdf_binary = base64.b64decode(pdf_data)
                _logger.info(f"PDF decodificado correctamente, tamaño={len(pdf_binary)} bytes")
            except Exception as e:
                _logger.error(f"❌ Error decodificando PDF: {e}")
                return {'error': 'Error decodificando PDF'}

            # =======================
            # Crear mail
            # =======================
            current_time = fields.Datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            email_body = f"""
Reporte Médico

{body}

---
Enviado el: {current_time}
Médico: {self.env.user.name}
            """.strip()
            _logger.info("Cuerpo de email preparado")

            mail_values = {
                'subject': subject,
                'body_html': f'<pre>{email_body}</pre>',
                'partner_ids': [(6, 0, partner_ids)],
                'author_id': self.env.user.partner_id.id,
                'email_from': self.env.user.email or 'admin@yourcompany.example.com',
            }

            mail = self.create(mail_values)
            _logger.info(f"Mail creado (ID: {mail.id})")

            # =======================
            # Crear attachment asociado al mail
            # =======================
            attachment = self.env['ir.attachment'].create({
                'name': pdf_name,
                'type': 'binary',
                'datas': base64.b64encode(pdf_binary).decode('utf-8'),
                'res_model': 'mail.mail',
                'res_id': mail.id,
                'mimetype': 'application/pdf',
                'public': False,  # Asegura que no sea accesible públicamente
            })
            _logger.info(f"Attachment creado: {attachment.name} (ID: {attachment.id})")

            # Vincular attachment al mail
            mail.attachment_ids = [(6, 0, [attachment.id])]

            # =======================
            # Enviar correo
            # =======================
            mail.send()
            _logger.info(f"✅ Reporte médico enviado a {len(partner_ids)} contactos")

            return {'success': True, 'message': f'Email enviado a {len(partner_ids)} contactos'}

        except Exception as e:
            _logger.error(f"❌ Error enviando reporte médico: {str(e)}", exc_info=True)
            return {'error': str(e)}
