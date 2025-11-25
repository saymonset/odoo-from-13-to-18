# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
import json

class TestPdfReport(models.Model):
    _name = 'test.pdf.report'
    _description = 'Modelo de prueba para reportes PDFMake'

    name = fields.Char("Nombre", default="Cliente de Prueba")
    amount = fields.Float("Importe", default=15899.50)
    active = fields.Boolean("Activo", default=True)
    partner_id = fields.Many2one('res.partner', string="Contacto")
    
    # Nuevos campos para el reporte de empleo
    is_employee_record = fields.Boolean("Es Registro de Empleado", default=False)
    employee_position = fields.Char("Cargo del Empleado")
    employee_start_date = fields.Date("Fecha de Inicio")
    employee_hours_per_week = fields.Integer("Horas Semanales", default=40)
    employee_work_schedule = fields.Char("Horario de Trabajo", default="Lunes a Viernes 9:00-18:00")
    employer_name = fields.Char("Nombre del Empleador")
    employer_position = fields.Char("Cargo del Empleador")
    employer_company = fields.Char("Empresa")
    
    def action_generate_employment_letter(self):
        """Acción para generar constancia de empleo"""
        self.ensure_one()
        
        # Asegurarnos de que tenemos valores por defecto
        employee_name = self.name or "Empleado"
        employee_position = self.employee_position or "Empleado"
        employee_start_date = self.employee_start_date.strftime('%d/%m/%Y') if self.employee_start_date else '01/01/2023'
        
        return {
            'type': 'ir.actions.client',
            'tag': 'pdfmake_download',
            'params': {
                'report_type': 'employment_letter',
                'employee_name': employee_name,
                'employee_position': employee_position,
                'employee_start_date': employee_start_date,
                'employee_hours': self.employee_hours_per_week or 40,
                'employee_work_schedule': self.employee_work_schedule or 'Lunes a Viernes 9:00-18:00',
                'employer_name': self.employer_name or 'Nombre del Empleador',
                'employer_position': self.employer_position or 'Gerente de RRHH',
                'employer_company': self.employer_company or 'Mi Empresa S.A.',
                'issue_date': fields.Date.today().strftime('%d/%m/%Y'),
                'record_id': self.id
            }
        }
    
    def action_generate_employment_letter_qweb(self):
        """Acción para generar constancia de empleo usando QWeb"""
        self.ensure_one()
        return {
            'type': 'ir.actions.report',
            'report_name': 'pdfmake.employment_letter_report',
            'report_type': 'qweb-pdf',
            'data': {
                'employee_name': self.name or "Empleado",
                'employee_position': self.employee_position or "Empleado",
                # ... otros datos
            }
        }
    def action_generate_hello_world(self):
        """Acción para generar reporte Hola Mundo"""
        self.ensure_one()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'pdfmake_download',
            'params': {
                'report_type': 'hello_world',
                'name': self.name or 'Test',
                'record_id': self.id
            }
        }