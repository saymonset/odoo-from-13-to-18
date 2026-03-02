from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import json
import logging

_logger = logging.getLogger(__name__)

class SessionState(models.Model):
    _name = 'session.state'
    _description = 'Estado de Sesión de Chatbot'
    _rec_name = 'session_id'
    _order = 'create_date desc'
    
    # Campo único para session_id
    session_id = fields.Char(
        string='ID de Sesión',
        required=True,
        unique=True,
        index=True,
        help='Identificador único de la sesión (generalmente de un chatbot o widget)'
    )
    
    # Campo JSON para el estado
    estado = fields.Json(
        string='Estado Actual',
        default=lambda self: self._default_estado(),
        help='Estado completo en formato JSON'
    )
    
    # Campos adicionales útiles
    create_date = fields.Datetime(string='Fecha de Creación', readonly=True)
    write_date = fields.Datetime(string='Última Actualización', readonly=True)
    
    # Campos derivados del JSON para facilitar búsquedas
    modo = fields.Char(
        string='Modo Actual',
        compute='_compute_campos_derivados',
        store=True,
        index=True
    )
    
    paso = fields.Char(
        string='Paso Actual',
        compute='_compute_campos_derivados',
        store=True,
        index=True
    )
    
    timestamp_estado = fields.Datetime(
        string='Timestamp del Estado',
        compute='_compute_campos_derivados',
        store=True
    )
    
    # Restricción para asegurar que session_id sea único
    _sql_constraints = [
        ('session_id_unique', 
         'UNIQUE(session_id)', 
         'El ID de sesión debe ser único'),
    ]
    
    
    @api.depends('estado')
    def _compute_campos_derivados(self):
        """Extrae campos del JSON para facilitar filtros"""
        for record in self:
            if record.estado:
                record.modo = record.estado.get('modo', '')
                record.paso = record.estado.get('paso', '')
                timestamp_str = record.estado.get('timestamp', '')
                if timestamp_str:
                    try:
                        record.timestamp_estado = fields.Datetime.from_string(
                            timestamp_str.replace('Z', '')
                        )
                    except:
                        record.timestamp_estado = False
                else:
                    record.timestamp_estado = False
            else:
                record.modo = ''
                record.paso = ''
                record.timestamp_estado = False
    
     
    # MÉTODO PARA GRABAR/ACTUALIZAR CON MERGE RECURSIVO
    @api.model
    def guardar_estado(self, session_id, estado_data):
        """
        Crea o actualiza un registro por session_id con merge recursivo
        
        Args:
            session_id (str): Identificador único de la sesión
            estado_data (dict): Datos del estado en formato JSON
        
        Returns:
            dict: Resultado de la operación
        """
        try:
            # Validar que estado_data sea un diccionario
            if not isinstance(estado_data, dict):
                raise ValidationError(_("Los datos del estado deben ser un diccionario"))
            
            # Buscar si ya existe un registro con ese session_id
            registro = self.search([('session_id', '=', session_id)], limit=1)
            
            if registro:
                # Obtener el estado actual
                estado_actual = registro.estado or {}
                
                # Función recursiva para hacer merge de diccionarios
                def merge_dicts(dict1, dict2):
                    """Fusión recursiva de diccionarios"""
                    result = dict1.copy()
                    
                    for key, value in dict2.items():
                        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                            # Si ambos son diccionarios, hacer merge recursivo
                            result[key] = merge_dicts(result[key], value)
                        else:
                            # Si no, reemplazar o agregar el nuevo valor
                            result[key] = value
                    
                    return result
                
                # Aplicar merge recursivo
                nuevo_estado = merge_dicts(estado_actual, estado_data)
                
                # Actualizar timestamp (siempre usar el más reciente)
                if 'timestamp' in estado_data:
                    nuevo_estado['timestamp'] = estado_data['timestamp']
                elif 'timestamp' not in nuevo_estado:
                    # Si no hay timestamp, agregar uno actual
                    nuevo_estado['timestamp'] = fields.Datetime.now().isoformat()
                
                # Asegurar que el estado tenga la estructura completa
                campos_requeridos = ['modo', 'paso', 'datos_paciente', 'timestamp']
                for campo in campos_requeridos:
                    if campo not in nuevo_estado:
                        # Si falta algún campo, usar valores por defecto
                        if campo == 'modo':
                            nuevo_estado[campo] = estado_data.get('modo', 'INICIO')
                        elif campo == 'paso':
                            nuevo_estado[campo] = estado_data.get('paso', 'BIENVENIDA')
                        elif campo == 'datos_paciente':
                            nuevo_estado[campo] = estado_data.get('datos_paciente', {})
                        elif campo == 'timestamp':
                            nuevo_estado[campo] = fields.Datetime.now().isoformat()
                
                # Actualizar registro existente
                registro.estado = nuevo_estado
                message = _("Estado actualizado correctamente")
                action = 'update'
            else:
                # Crear nuevo registro con estructura completa
                nuevo_estado = estado_data.copy()
                
                # Asegurar que el nuevo estado tenga la estructura completa
                if 'modo' not in nuevo_estado:
                    nuevo_estado['modo'] = 'INICIO'
                if 'paso' not in nuevo_estado:
                    nuevo_estado['paso'] = 'BIENVENIDA'
                if 'datos_paciente' not in nuevo_estado:
                    nuevo_estado['datos_paciente'] = {}
                if 'timestamp' not in nuevo_estado:
                    nuevo_estado['timestamp'] = fields.Datetime.now().isoformat()
                
                registro = self.create({
                    'session_id': session_id,
                    'estado': nuevo_estado
                })
                message = _("Estado creado correctamente")
                action = 'create'
            
            # Forzar el cálculo de campos derivados inmediatamente
            registro._compute_campos_derivados()
            
            # Retornar respuesta
            return {
                'success': True,
                'message': message,
                'action': action,
                'session_id': session_id,
                'record_id': registro.id,
                'write_date': registro.write_date,
                'estado_actual': registro.estado
            }
            
        except Exception as e:
            _logger.error(f"Error al guardar estado: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'session_id': session_id
            }


    # También actualiza el método _default_estado para incluir todos los campos necesarios
    @api.model
    def _default_estado(self):
        """Valor por defecto para el estado"""
        return {
            "modo": "INICIO",
            "paso": "BIENVENIDA",
            "datos_paciente": {},
            "timestamp": fields.Datetime.now().isoformat()
        }
    
    # MÉTODO PARA CONSULTAR
    @api.model
    def consultar_por_session(self, session_id):
        """
        Consulta un registro por su session_id
        
        Args:
            session_id (str): Identificador de la sesión
        
        Returns:
            dict: Datos del registro o None si no existe
        """
        try:
            registro = self.search([('session_id', '=', session_id)], limit=1)
            
            if not registro:
                return {
                    'success': False,
                    'session_id': session_id,
                    'message': _("No se encontró registro con ese session_id"),
                    'found': False
                }
            
            # Retornar datos del registro
            return {
                'success': True,
                'found': True,
                'session_id': registro.session_id,
                'estado': registro.estado,
                'modo': registro.modo,
                'paso': registro.paso,
                'timestamp_estado': registro.timestamp_estado,
                'create_date': registro.create_date,
                'write_date': registro.write_date,
                'record_id': registro.id
            }
            
        except Exception as e:
            _logger.error(f"Error al consultar estado: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'session_id': session_id
            }
    
    # MÉTODO PARA LIMPIAR SESIONES ANTIGUAS (opcional)
    @api.model
    def limpiar_sesiones_antiguas(self, horas=24):
        """
        Elimina registros más antiguos que X horas
        
        Args:
            horas (int): Número de horas para conservar
        
        Returns:
            dict: Resultado de la limpieza
        """
        try:
            from datetime import datetime, timedelta
            
            fecha_limite = datetime.now() - timedelta(hours=horas)
            registros_antiguos = self.search([
                ('create_date', '<', fecha_limite)
            ])
            
            cantidad = len(registros_antiguos)
            registros_antiguos.unlink()
            
            return {
                'success': True,
                'eliminados': cantidad,
                'message': _("Se eliminaron %d sesiones antiguas") % cantidad
            }
            
        except Exception as e:
            _logger.error(f"Error al limpiar sesiones: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    # Sobrescribir método create para validaciones adicionales
    @api.model
    def create(self, vals):
        # Validar formato del session_id
        if 'session_id' in vals and not vals['session_id']:
            raise ValidationError(_("El session_id no puede estar vacío"))
        
        return super(SessionState, self).create(vals)
    
    def write(self, vals):
        # Validar que no se pueda cambiar el session_id una vez creado
        if 'session_id' in vals:
            for record in self:
                if record.session_id != vals['session_id']:
                    raise ValidationError(
                        _("No se puede modificar el session_id de una sesión existente")
                    )
        
        return super(SessionState, self).write(vals)
    
    # MÉTODO PARA ACTUALIZAR SOLO CIERTOS CAMPOS
    @api.model
    def actualizar_estado_parcial(self, session_id, campos_actualizar):
        """
        Actualiza solo campos específicos del estado sin perder datos existentes
        
        Args:
            session_id (str): Identificador único de la sesión
            campos_actualizar (dict): Campos a actualizar en formato {campo: valor}
        
        Returns:
            dict: Resultado de la operación
        """
        try:
            # Buscar si ya existe un registro con ese session_id
            registro = self.search([('session_id', '=', session_id)], limit=1)
            
            if not registro:
                return {
                    'success': False,
                    'error': _("No se encontró sesión con ese ID"),
                    'session_id': session_id
                }
            
            # Obtener el estado actual
            estado_actual = registro.estado or {}
            
            # Actualizar solo los campos especificados
            for campo, valor in campos_actualizar.items():
                if campo == 'datos_paciente' and isinstance(valor, dict):
                    # Para el campo 'datos_paciente', hacer merge recursivo
                    if 'datos_paciente' not in estado_actual:
                        estado_actual['datos_paciente'] = {}
                    
                    # Función para merge recursivo
                    def merge_datos(datos1, datos2):
                        result = datos1.copy()
                        for k, v in datos2.items():
                            if k in result and isinstance(result[k], dict) and isinstance(v, dict):
                                result[k] = merge_datos(result[k], v)
                            else:
                                result[k] = v
                        return result
                    
                    estado_actual['datos_paciente'] = merge_datos(estado_actual['datos_paciente'], valor)
                else:
                    # Para otros campos, actualizar directamente
                    estado_actual[campo] = valor
            
            # Actualizar timestamp
            estado_actual['timestamp'] = fields.Datetime.now().isoformat()
            
            # Guardar cambios
            registro.estado = estado_actual
            
            # Forzar el cálculo de campos derivados
            registro._compute_campos_derivados()
            
            return {
                'success': True,
                'message': _("Estado actualizado parcialmente"),
                'session_id': session_id,
                'record_id': registro.id,
                'estado_actual': registro.estado
            }
            
        except Exception as e:
            _logger.error(f"Error al actualizar estado parcial: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'session_id': session_id
            }
