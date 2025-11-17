from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo import _
import logging 
_logger = logging.getLogger(__name__)

class Diagnosis(models.Model):
    _name = 'a_hospital.diagnosis'
    _description = 'Diagnosis'
    
    # Campos
    attachment_ids = fields.Many2many(
        'ir.attachment',
        string='Archivos Adjuntos',
    )
    
    visit_id = fields.Many2one(
        comodel_name='a_hospital.visit',
        string='Visit',
    )

    doctor_id = fields.Many2one(
        comodel_name='a_hospital.doctor',
        string='Doctor',
    )

    disease_id = fields.Many2one(
        comodel_name='a_hospital.disease',
        string='Disease',
    )

    patient_id = fields.Many2one(
        comodel_name='a_hospital.patient',
        string='Patient',
    )

    description = fields.Text(
        string='Diagnosis Description',
    )

    is_approved = fields.Boolean(
        string='Approved',
        default=False,
    )

    doctor_approved = fields.Char(
        string='Doctor approved'
    )

    disease_type_id = fields.Many2one(
        related='disease_id.disease_type_id',
        comodel_name='a_hospital.disease.type',
        string='Disease Type',
        store=True,
        readonly=True
    )

    def action_open_voice_recorder(self):
        """Abrir el grabador de voz existente de chatter_voice_note"""
        self.ensure_one()
        
        _logger.info(f"🔍 Diagnóstico actual: ID={self.id}")
            
        # Si es un registro nuevo, guardarlo primero
        if not self.id:
            if not self.visit_id or not self.doctor_id or not self.patient_id:
                raise ValidationError(_("Debe completar los campos de visita, doctor y paciente antes de grabar."))
            
            create_vals = {
                'visit_id': self.visit_id.id,
                'doctor_id': self.doctor_id.id,
                'patient_id': self.patient_id.id,
                'description': self.description or '',
            }
            if self.disease_id:
                create_vals['disease_id'] = self.disease_id.id
                
            self = self.create(create_vals)
            
            self = self.env['a_hospital.diagnosis'].browse(self.id)
            
            _logger.info(f"🎯 Enviando res_id: {self.id} al grabador de voz")
        
        # Retornar la acción del cliente para abrir el grabador
        return {
            'type': 'ir.actions.client',
            'tag': 'chatter_voice_note.audio_to_text',
            'target': 'new',
            'name': 'Grabador de Voz',
            'params': {
                'res_model': self._name,
                'res_id': self.id,
            }
        }

    # ⭐⭐ MÉTODO CRÍTICO PARA ACTUALIZAR LA DESCRIPCIÓN
    @api.model
    def update_description_from_voice(self, res_id, text):
        """Método llamado por el grabador de voz para actualizar la descripción"""
        diagnosis = self.browse(res_id)
        if diagnosis.exists():
            diagnosis.write({'description': text})
            _logger.info(f"✅ Descripción actualizada para diagnóstico {res_id}: {text}")
            return True
        _logger.error(f"❌ No se pudo encontrar diagnóstico con ID: {res_id}")
        return False

    # Método alternativo por si el anterior no funciona
    def write_description(self, text):
        """Método alternativo para escribir la descripción"""
        self.ensure_one()
        if text and text.strip():
            self.description = text
            _logger.info(f"✅ Descripción escrita para diagnóstico {self.id}")
            return True
        return False