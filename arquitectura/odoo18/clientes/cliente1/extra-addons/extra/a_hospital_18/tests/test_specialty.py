# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

class TestSpecialty(TransactionCase):
    
    def setUp(self):
        super(TestSpecialty, self).setUp()
        # Crear datos de prueba
        self.Specialty = self.env['a_hospital.specialty']
        self.test_specialty = self.Specialty.create({
            'name': 'Cardiology',
            'description': 'Heart-related treatments'
        })
    
    def test_01_create_specialty(self):
        """Test creación de una especialidad"""
        # Verificar que se creó correctamente
        self.assertEqual(self.test_specialty.name, 'Cardiology')
        self.assertEqual(self.test_specialty.description, 'Heart-related treatments')
        
        # Verificar que el nombre es obligatorio
        with self.assertRaises(ValidationError):
            self.Specialty.create({'name': False})
    
    def test_02_name_uniqueness(self):
        """Test que verifica la unicidad del nombre"""
        # Intentar crear una especialidad con el mismo nombre
        with self.assertRaises(ValidationError):
            self.Specialty.create({
                'name': 'Cardiology',  # Mismo nombre
                'description': 'Different description'
            })
    
    def test_03_name_length_validation(self):
        """Test que verifica la longitud del nombre"""
        # Intentar crear una especialidad con nombre muy largo
        long_name = 'A' * 101  # Nombre de más de 100 caracteres
        
        with self.assertRaises(ValidationError):
            self.Specialty.create({
                'name': long_name,
                'description': 'Test description'
            })
    
    def test_04_search_specialty(self):
        """Test de búsqueda de especialidades"""
        # Buscar especialidad por nombre
        specialties = self.Specialty.search([('name', '=', 'Cardiology')])
        self.assertEqual(len(specialties), 1)
        self.assertEqual(specialties[0].id, self.test_specialty.id)
        
        # Buscar especialidad que no existe
        specialties = self.Specialty.search([('name', '=', 'NonExistent')])
        self.assertEqual(len(specialties), 0)
    
    def test_05_update_specialty(self):
        """Test de actualización de especialidad"""
        # Actualizar descripción
        self.test_specialty.write({
            'description': 'Updated description'
        })
        self.assertEqual(self.test_specialty.description, 'Updated description')
        
        # Verificar que el nombre no se puede cambiar a vacío
        with self.assertRaises(ValidationError):
            self.test_specialty.write({'name': ''})