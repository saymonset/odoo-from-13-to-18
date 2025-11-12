from odoo import models, fields, api
import base64
import logging

_logger = logging.getLogger(__name__)

class MailMail(models.Model):
    _inherit = 'mail.mail'
    
    @api.model
    def create_and_send_medical_report(self, email_data):
        try:
            # Extraer datos
            pdf_data = email_data.get('pdf_data')
            pdf_name = email_data.get('pdf_name', 'reporte_medico.pdf')
            contacts = email_data.get('contacts', [])
            subject = email_data.get('subject', 'Reporte Médico')
            body = email_data.get('body', '')
            
            if not pdf_data or not contacts:
                return {'error': 'Datos incompletos'}
            
            # Decodificar PDF
            pdf_binary = base64.b64decode(pdf_data)
            
            # Preparar destinatarios
            partner_ids = []
            for contact in contacts:
                partner_id = contact.get('partner_id')
                if partner_id:
                    partner_ids.append(partner_id)
            
            if not partner_ids:
                return {'error': 'No hay destinatarios válidos'}
            
            # Crear attachment
            attachment = self.env['ir.attachment'].create({
                'name': pdf_name,
                'type': 'binary',
                'datas': base64.b64encode(pdf_binary),
                'res_model': 'mail.compose.message',
                'res_id': 0,
            })
            
            # Crear y enviar email
            mail_values = {
                'subject': subject,
                'body_html': f'<pre>{body}</pre>',
                'attachment_ids': [(6, 0, [attachment.id])],
                'partner_ids': [(6, 0, partner_ids)],
                'author_id': self.env.user.partner_id.id,
            }
            
            mail = self.create(mail_values)
            mail.send()
            d
            _logger.info(f"✅ Reporte médico enviado a {len(partner_ids)} contactos")
            
            return {'success': True, 'message': f'Email enviado a {len(partner_ids)} contactos'}
            
        except Exception as e:
            _logger.error(f"❌ Error enviando reporte médico: {str(e)}")
            return {'error': str(e)}