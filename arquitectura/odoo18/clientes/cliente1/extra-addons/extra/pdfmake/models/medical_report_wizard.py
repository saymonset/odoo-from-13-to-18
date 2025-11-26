# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
import json
import base64

class MedicalReportWizard(models.TransientModel):
    _name = 'medical.report.wizard'
    _description = 'Wizard para generar reportes médicos con QWeb'

    patient_name = fields.Char(string="Nombre del Paciente", required=True)
    patient_age = fields.Integer(string="Edad del Paciente")
    patient_gender = fields.Selection([
        ('male', 'Masculino'),
        ('female', 'Femenino'),
        ('other', 'Otro')
    ], string="Género")
    
    diagnosis = fields.Text(string="Diagnóstico", required=True)
    recommendations = fields.Text(string="Recomendaciones")
    treatment = fields.Text(string="Tratamiento")
    
    doctor_name = fields.Char(string="Nombre del Médico", default=lambda self: self._get_default_doctor())
    doctor_specialty = fields.Char(string="Especialidad")
    medical_center = fields.Char(string="Centro Médico", default=lambda self: self._get_default_medical_center())
    
    # Nuevos campos para integración
    report_type = fields.Selection([
        ('basic', 'Reporte Básico'),
        ('detailed', 'Reporte Detallado'),
        ('prescription', 'Receta Médica')
    ], string="Tipo de Reporte", default='basic')
    
    include_signature = fields.Boolean(string="Incluir Firma", default=True)
    
    def _get_default_doctor(self):
        user = self.env.user
        return user.name
    
    def _get_default_medical_center(self):
        company = self.env.company
        return company.name
    
    def action_generate_medical_report(self):
        """Genera reporte médico usando QWeb de PDFMake"""
        self.ensure_one()
        
        medical_data = {
            'patient_name': self.patient_name,
            'patient_age': self.patient_age,
            'patient_gender': dict(self._fields['patient_gender'].selection).get(self.patient_gender, ''),
            'diagnosis': self.diagnosis,
            'recommendations': self.recommendations or 'Seguir las indicaciones del médico.',
            'treatment': self.treatment or 'Tratamiento según diagnóstico.',
            'doctor_name': self.doctor_name,
            'doctor_specialty': self.doctor_specialty or 'Médico General',
            'medical_center': self.medical_center,
            'report_type': self.report_type,
            'include_signature': self.include_signature,
            'issue_date': datetime.now().strftime('%d/%m/%Y'),
            'current_datetime': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'record_id': self.id
        }
        
        # Llamar al controlador de PDFMake para generar el PDF
        return {
            'type': 'ir.actions.act_url',
            'url': f'/pdfmake/medical-report-qweb?{self._prepare_url_params(medical_data)}',
            'target': 'new'
        }
    
    def _prepare_url_params(self, data):
        """Prepara parámetros para la URL"""
        params = []
        for key, value in data.items():
            if value:
                params.append(f"{key}={value}")
        return '&'.join(params)
    
    def action_send_to_chatter_module(self):
        """Envía el PDF generado al módulo Chatter Voice Note"""
        self.ensure_one()
        
        medical_data = {
            'patient_name': self.patient_name,
            'patient_age': self.patient_age,
            'patient_gender': dict(self._fields['patient_gender'].selection).get(self.patient_gender, ''),
            'diagnosis': self.diagnosis,
            'recommendations': self.recommendations,
            'treatment': self.treatment,
            'doctor_name': self.doctor_name,
            'doctor_specialty': self.doctor_specialty,
            'medical_center': self.medical_center,
            'report_type': self.report_type,
            'include_signature': self.include_signature,
            'issue_date': datetime.now().strftime('%d/%m/%Y'),
            'current_datetime': datetime.now().strftime('%d/%m/%Y %H:%M'),
        }
        
        # Generar PDF usando el servicio de PDFMake
        pdf_content = self.env['pdfmake.service'].generate_medical_pdf(medical_data)
        
        # Aquí integrarías con el módulo Chatter Voice Note
        # Por ejemplo, adjuntar el PDF a un registro específico
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'PDF Generado',
                'message': f'Reporte médico de {self.patient_name} generado exitosamente',
                'type': 'success',
                'sticky': False,
            }
        }