from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import json
import logging
import re
from datetime import datetime
from odoo.addons.chat_bot_integra.controllers.chatbot_utils import ChatBotUtils

_logger = logging.getLogger(__name__)

class SessionState(models.Model):
    _name = 'chatbot.session'
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

    last_activity = fields.Datetime(string='Última Actividad', default=lambda self: fields.Datetime.now())
    
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
    
    pasos_pendientes = fields.Json(
        string='Pasos Pendientes',
        default=list,
        help='Lista ordenada de pasos del flujo pendientes de procesar'
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

    # ==================================================================
    #  NUEVOS MÉTODOS PRIVADOS PARA INTEGRACIÓN CON IA
    # ==================================================================
    def _get_gpt_service(self):
        """Retorna el servicio GPT configurado (con sudo para evitar permisos)."""
        return self.env['gpt.service'].sudo()

    def _generar_pregunta_amigable(self, nombre_mostrar, tipo=None, max_tokens=100):
        """
        Convierte un nombre de campo (ej: 'Teléfono') en una pregunta amigable.
        Si la IA falla, devuelve un fallback.
        """
        service = self._get_gpt_service()
        pregunta = ""
        try:
            resultado = service.GenerarPreguntaIntegraia(nombre_mostrar, max_tokens=max_tokens)
            if resultado.get('status') == 'success':
                pregunta = resultado['generated_question']
        except Exception as e:
            _logger.error(f"Error generando pregunta amigable para '{nombre_mostrar}': {e}")
        
        if not pregunta:
            # Fallback humanizado
            pregunta = f"Por favor, ingresa tu {nombre_mostrar.lower()}"
            
        # --- MEJORA: Agregar instrucción de salto para imágenes/archivos ---
        if tipo in ['image', 'file']:
            if "\n" in pregunta:
                pregunta += "\n(O escribe *'saltar'* si no la tienes a mano)"
            else:
                pregunta += "\n\n(O escribe *'saltar'* si no la tienes a mano)"
                
        return pregunta

    def _validar_con_ia(self, valor, tipo_dato, paso, nombre_mostrar):
        """
        Valida un valor usando el servicio GPT que retorna mensajes de error amigables.
        Retorna (valido, valor_transformado, mensaje_error)
        """
        service = self._get_gpt_service()
        try:
            resultado = service.validar_valor_amigable(
                valor=valor,
                tipo_dato=tipo_dato,
                paso=paso,
                nombre_mostrar=nombre_mostrar,
                max_tokens=120
            )
            return (
                resultado.get('success', False),
                resultado.get('valor_transformado'),
                resultado.get('mensaje', '')
            )
        except Exception as e:
            _logger.error(f"Error en validación con IA: {e}")
            # Fallback: usar la validación tradicional del ChatBotUtils
            utils = ChatBotUtils()
            valido, resultado_trad = utils.validar_valor(valor, tipo_dato, paso)
            if valido:
                return True, resultado_trad, ''
            else:
                return False, None, resultado_trad  # mensaje original (posiblemente robótico)

    # ==================================================================
    #  MÉTODOS ORIGINALES (modificados para usar IA)
    # ==================================================================
    @api.model
    def iniciar_flujo(self, session_id, flow_name, steps, equipo_asignado):
        """
        Inicia un flujo para una sesión, guardando los pasos pendientes y estableciendo el primer paso.
        steps: lista de diccionarios con la definición de cada paso.
        AHORA: se genera una pregunta amigable para el primer paso usando IA.
        """
        # --- MEJORA IA: generar pregunta amigable para el primer paso ---
        if steps:
            primer_paso = steps[0].copy()
            nombre_original = primer_paso.get('nombre_mostrar', '')
            pregunta_amigable = self._generar_pregunta_amigable(nombre_original, tipo=primer_paso.get('tipo_dato'))
            primer_paso['mensaje_prompt'] = pregunta_amigable
            primer_paso['nombre_mostrar'] = pregunta_amigable  # opcional, para mostrarlo
            steps[0] = primer_paso

        registro = self.search([('session_id', '=', session_id)], limit=1)
        if not registro:
            estado_inicial = {
                'modo': 'FLUJO',
                'paso': steps[0]['nombre_interno'] if steps else 'SIN_PASOS',
                'nombre_mostrar': steps[0]['nombre_mostrar'] if steps else 'SIN_PASOS',
                'tipo_dato': steps[0]['tipo_dato'] if steps else 'SIN_PASOS',
                'mensaje_prompt': steps[0]['mensaje_prompt'] if steps else 'SIN_PASOS',
                'mensaje_error': steps[0]['mensaje_error'] if steps else 'SIN_PASOS',
                'es_requerido': steps[0]['es_requerido'] if steps else 'SIN_PASOS',
                'datos_paciente': {'equipo_asignado': equipo_asignado},
                'timestamp': fields.Datetime.now().isoformat()
            }
            vals = {
                'session_id': session_id,
                'estado': estado_inicial,
                'pasos_pendientes': steps
            }
            registro = self.create(vals)
            action = 'create'
        else:
            nuevo_estado = registro.estado.copy() if registro.estado else {}
            nuevo_estado.update({
                'modo': 'FLUJO',
                'paso': steps[0]['nombre_interno'] if steps else 'SIN_PASOS',
                'nombre_mostrar': steps[0]['nombre_mostrar'] if steps else 'SIN_PASOS',
                'tipo_dato': steps[0]['tipo_dato'] if steps else 'SIN_PASOS',
                'mensaje_prompt': steps[0]['mensaje_prompt'] if steps else 'SIN_PASOS',
                'mensaje_error': steps[0]['mensaje_error'] if steps else 'SIN_PASOS',
                'es_requerido': steps[0]['es_requerido'] if steps else 'SIN_PASOS',
                'datos_paciente': {},  # Reiniciamos datos (opcional)
                'timestamp': fields.Datetime.now().isoformat()
            })
            registro.write({
                'estado': nuevo_estado,
                'pasos_pendientes': steps,
                'last_activity': fields.Datetime.now()
            })
            action = 'update'

        return {
            'success': True,
            'action': action,
            'session_id': session_id,
            'record_id': registro.id,
            'paso_actual': registro.estado['paso'] if registro.estado else None,
            'pasos_pendientes': registro.pasos_pendientes
        }

    def procesar_paso(self, session_id, valor, paso, conversation_id, account_id):
        _logger.info("Iniciando procesar_paso para session_id: %s", session_id)
        registro = self.sudo().search([('session_id', '=', session_id)], limit=1)
        
        if not registro:
            _logger.info("Sesión no encontrada: %s. Generando mensaje sin sesión.", session_id)
            mensaje = self._generar_mensaje_sin_sesion(valor)
            return {
                'success': True,
                'texto_para_usuario': mensaje,
                'text': mensaje,
                'modo': 'COMPLETADO',
                'session_id': session_id,
                'conversation_id': conversation_id,
                'account_id': account_id
            }

        # --- MEJORA: Si la sesión ya estaba completada, la reiniciamos ---
        if registro.modo == 'COMPLETADO':
            _logger.info("Sesión previa 'COMPLETADO' encontrada. Eliminando para iniciar proceso limpio.")
            registro.sudo().unlink()
            mensaje = self._generar_mensaje_sin_sesion(valor)
            return {
                'success': True,
                'texto_para_usuario': mensaje,
                'text': mensaje,
                'modo': 'MENU_PRINCIPAL',
                'session_id': session_id,
                'conversation_id': conversation_id,
                'account_id': account_id
            }
        
        _logger.info("Sesión encontrada (ID: %s). Modo actual: %s", registro.id, registro.modo)

        # ----- EXPIRACIÓN POR INACTIVIDAD (10 minutos) -----
        delta = fields.Datetime.now() - registro.last_activity
        if delta.total_seconds() > 600:
            _logger.info("Sesión expirada por inactividad: %s (última actividad hace %d segundos)", session_id, delta.total_seconds())
            mensaje = self._generar_mensaje_expirado(valor)
            registro.unlink()
            return {
                'success': True,
                'finalizado': False,
                'modo': 'COMPLETADO',
                'texto_para_usuario': mensaje,
                'text': mensaje,
                'session_id': session_id,
                'conversation_id': conversation_id,
                'account_id': account_id,
            }

        # Obtener datos del paso actual antes de detectar salida
        paso_actual = registro.pasos_pendientes[0] if registro.pasos_pendientes else {}
        tipo = paso_actual.get('tipo_dato', 'text')
        campo_destino = paso_actual.get('campo_destino', '')

        # ----- 1. DETECTAR SALIDA -----
        # Si es una URL de imagen válida, un número de teléfono o palabras clave de flujo, no evaluamos intención de salida por IA
        es_url_imagen = re.match(r'^https?://', valor) and (tipo == 'image' or any(ext in valor.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']))
        es_telefono_claro = re.match(r'^\+?[0-9]{7,15}$', valor.strip())
        es_palabra_flujo = valor.strip().lower() in ['listo', 'no', 'continuar', 'omitir', 'siguiente']
        
        if es_url_imagen or es_telefono_claro or es_palabra_flujo:
            es_salida, mensaje_salida = False, ""
            _logger.info("Omitiendo detección de salida por IA (es imagen, teléfono o palabra de control: %s)", valor)
        else:
            es_salida, mensaje_salida = self._detectar_intencion_salida(valor)
        
        # Protección extendida: si estamos en un paso de carga de archivos/fotos, "listo" o "no" nunca es salida
        if es_salida and (tipo in ['image', 'file'] or 'foto' in campo_destino or 'imagen' in campo_destino):
            _logger.info("Protección: suprimiendo intención de salida en paso de fotos/archivos")
            es_salida = False
            mensaje_salida = ""
            
        if es_salida:
            _logger.info("Marcando sesión como COMPLETADO (por intención de salida): %s", registro.session_id)
            registro.sudo().write({'modo': 'COMPLETADO'})
            return {
                'success': True,
                'finalizado': True,
                'modo': 'COMPLETADO',
                'texto_para_usuario': mensaje_salida,
                'text': mensaje_salida,
                'session_id': session_id,
                'conversation_id': conversation_id,
                'account_id': account_id
            }

        # Actualizar última actividad inmediatamente
        registro.write({'last_activity': fields.Datetime.now()})

        if not registro.pasos_pendientes:
            mensaje = self._generar_mensaje_sin_pasos(valor)
            return {
                'success': True,
                'finalizado': False,
                'modo': 'COMPLETADO',     # Cambiamos de COMPLETADO 
                'texto_para_usuario': mensaje,
                'text': mensaje,
                'session_id': session_id,
                'conversation_id': conversation_id,
                'account_id': account_id,
            }

        # (Ya definidos arriba)
        # paso_actual = registro.pasos_pendientes[0]
        # tipo = paso_actual.get('tipo_dato', 'text')
        # campo_destino = paso_actual.get('campo_destino')
        
        es_paso_telefono = paso_actual.get('es_paso_telefono', False) or campo_destino == 'solicitar_phone'

        nombre_mostrar = paso_actual.get('nombre_mostrar', '')
        
        # Palabras clave para saltar pasos (especialmente imágenes) o finalizar carga
        es_palabra_salto = valor.strip().lower() in ['no', 'omitir', 'saltar', 'no tengo', 'no la tengo', 'después', 'luego', 'n', 'skip']
        es_finalizar_carga = valor.strip().lower() in ['listo', 'finalizar', 'terminar', 'ya está', 'ya esta']

        # --- LÓGICA DE SALTO PARA IMÁGENES/ARCHIVOS (Simples) ---
        if tipo in ['image', 'file'] and es_palabra_salto and campo_destino != 'solicitar_imagenes_adicionales':
            _logger.info("El usuario decidió saltar el paso de imagen/archivo: %s", campo_destino)
            valido = True
            resultado = "No proporcionada"
            mensaje_error = ""
        # --- NUEVA LÓGICA: BUCLE DE CARGA MÚLTIPLE PARA IMÁGENES ADICIONALES ---
        elif campo_destino == 'solicitar_imagenes_adicionales':
            # 1. Intentar validar como imagen primero
            valido_img, resultado_img, _ = self._validar_con_ia(valor, 'image', paso, nombre_mostrar)
            
            if valido_img:
                # Es una imagen válida, la agregamos a la lista
                estado_actual = registro.estado or {}
                datos_p = estado_actual.get('datos_paciente', {})
                
                # Inicializar o recuperar lista
                imgs_adicionales = datos_p.get('solicitar_imagenes_adicionales', [])
                if isinstance(imgs_adicionales, str):
                    try:
                        imgs_adicionales = json.loads(imgs_adicionales)
                    except:
                        imgs_adicionales = [imgs_adicionales] if imgs_adicionales else []
                
                if resultado_img not in imgs_adicionales:
                    imgs_adicionales.append(resultado_img)
                
                datos_p['solicitar_imagenes_adicionales'] = imgs_adicionales
                estado_actual['datos_paciente'] = datos_p
                estado_actual['timestamp'] = fields.Datetime.now().isoformat()
                
                registro.write({'estado': estado_actual})
                
                # Respuesta pidiendo más o finalizar
                mensaje_recibido = f"¡Excelente! He recibido la imagen ✅. ¿Deseas agregar otra imagen? O si ya finalizastes, escribe *'listo'* para continuar."
                return {
                    'success': True,
                    'finalizado': False,
                    'modo': 'FLUJO',
                    'texto_para_usuario': mensaje_recibido,
                    'text': mensaje_recibido,
                    'session_id': session_id,
                    'conversation_id': conversation_id,
                    'account_id': account_id,
                    'paso_actual': paso,
                    'mensaje_prompt': mensaje_recibido,
                }
            else:
                # Ver si el usuario quiere terminar o no tiene la imagen
                if not (es_palabra_salto or es_finalizar_carga):
                    res_fin = self._get_gpt_service().detectar_intencion_finalizar_carga(valor)
                
                if es_palabra_salto or es_finalizar_carga or res_fin.get('termino'):
                    # El usuario terminó de subir fotos o saltó el paso
                    _logger.info("El usuario decidió finalizar carga de imágenes o saltar el paso.")
                    resultado = registro.estado.get('datos_paciente', {}).get(campo_destino, [])
                    valido = True
                    # Continuamos con la lógica normal de avance
                else:
                    # Ni es imagen ni quiere terminar, error amigable
                    valido, resultado, mensaje_error = self._validar_con_ia(valor, tipo, paso, nombre_mostrar)
                    if not valido:
                        return {
                            'success': True,
                            'finalizado': False,
                            'modo': 'FLUJO',
                            'texto_para_usuario': mensaje_error,
                            'text': mensaje_error,
                            'session_id': session_id,
                            'conversation_id': conversation_id,
                            'account_id': account_id,
                            'paso_actual': paso,
                            'mensaje_prompt': paso_actual.get('mensaje_prompt'),
                        }
        else:
            # 1. Intentar validación tradicional primero (más rápida y sin costo)
            _logger.info("Procesando valor '%s' para paso '%s' (tipo: %s)", valor, paso, tipo)
            utils_trad = ChatBotUtils()
            valido_trad, resultado_trad = utils_trad.validar_valor(valor, tipo, paso)
            
            if valido_trad:
                _logger.info("Validación tradicional exitosa para '%s': %s", paso, resultado_trad)
                valido = True
                resultado = resultado_trad
                mensaje_error = ""
            else:
                _logger.info("Validación tradicional falló para '%s', intentando con IA...", paso)
                # 2. Si falla la tradicional, intentar con IA para extraer valor o generar error amigable
                valido, resultado, mensaje_error = self._validar_con_ia(valor, tipo, paso, nombre_mostrar)

            if not valido:
                return {
                    'success': True,
                    'finalizado': False,
                    'modo': 'FLUJO',
                    'texto_para_usuario': mensaje_error,
                    'text': mensaje_error,
                    'session_id': session_id,
                    'conversation_id': conversation_id,
                    'account_id': account_id,
                    'paso_actual': paso_actual.get('nombre_interno'),
                    'mensaje_prompt': paso_actual.get('mensaje_prompt'),
                }

        estado_actual = registro.estado or {}
        if 'datos_paciente' not in estado_actual:
            estado_actual['datos_paciente'] = {}
        _logger.info("Guardando resultado en datos_paciente: %s = %s", campo_destino, resultado)
        estado_actual['datos_paciente'][campo_destino] = resultado

        nuevos_pasos = registro.pasos_pendientes[1:]
        _logger.info("Nuevos pasos pendientes iniciales: %d", len(nuevos_pasos))

        # Auto‑rellenado por teléfono
        utils = ChatBotUtils()
        if es_paso_telefono:
            _logger.info("Paso de teléfono detectado. Buscando partner para: %s", valor)
            partner = utils.find_partner_by_phone(self.env, valor)
            if partner:
                _logger.info("Partner encontrado: %s (ID: %s)", partner.name, partner.id)
                auto_map = {}
                if partner.name:
                    auto_map['solicitar_name'] = partner.name
                if partner.vat:
                    auto_map['solicitar_vat'] = partner.vat
                if partner.birthdate:
                    try:
                        auto_map['solicitar_birthdate'] = partner.birthdate.isoformat()
                    except Exception as e:
                        _logger.warning("Error al formatear fecha de nacimiento: %s", e)
                auto_map['solicitar_es_paciente_nuevo'] = 'no'
                
                for campo, valor_auto in auto_map.items():
                    estado_actual['datos_paciente'][campo] = valor_auto
                
                # Filtrar pasos que ya tenemos
                viejos_pasos_count = len(nuevos_pasos)
                nuevos_pasos = [p for p in nuevos_pasos if p.get('campo_destino') not in auto_map]
                _logger.info("Auto-relleno completado. Pasos eliminados: %d", viejos_pasos_count - len(nuevos_pasos))
            else:
                _logger.info("No se encontró partner para el teléfono: %s", valor)
                estado_actual['datos_paciente']['solicitar_es_paciente_nuevo'] = 'si'

        if nuevos_pasos:
            _logger.info("Siguiente paso detectado: %s", nuevos_pasos[0].get('campo_destino'))
            siguiente = nuevos_pasos[0].copy()
            pregunta_amigable = self._generar_pregunta_amigable(siguiente.get('nombre_mostrar', ''), tipo=siguiente.get('tipo_dato'))
            siguiente['mensaje_prompt'] = pregunta_amigable
            siguiente['nombre_mostrar'] = pregunta_amigable
            nuevos_pasos[0] = siguiente
            
            estado_actual.update({
                'paso': siguiente.get('campo_destino'),
                'nombre_mostrar': pregunta_amigable,
                'tipo_dato': siguiente.get('tipo_dato'),
                'mensaje_prompt': pregunta_amigable,
                'es_requerido': siguiente.get('es_requerido'),
                'modo': 'FLUJO',
                'timestamp': fields.Datetime.now().isoformat()
            })
            
            _logger.info("Actualizando registro con nuevos pasos y estado. Nuevo paso: %s", estado_actual['paso'])
            registro.write({
                'estado': estado_actual,
                'pasos_pendientes': nuevos_pasos
            })
            
            return {
                'success': True,
                'texto_para_usuario': pregunta_amigable,
                'text': pregunta_amigable,
                'modo': registro.modo,
                'paso_actual': estado_actual['paso'],
                'session_id': session_id,
                'conversation_id': conversation_id,
                'account_id': account_id
            }
        else:
            # Flujo completado
            _logger.info("Flujo completado. Iniciando capturar_lead.")
            lead_resultado = self.capturar_lead(estado_actual['datos_paciente'])
            _logger.info("Resultado de capturar_lead: %s", lead_resultado.get('success'))
            
            # Marcamos la sesión como COMPLETADA pero NO la eliminamos aún para dejar que n8n procese
            _logger.info("Marcando sesión como COMPLETADO: %s", session_id)
            registro.sudo().write({'modo': 'COMPLETADO'})
            
            mensaje_final = self._generar_mensaje_finalizacion(estado_actual['datos_paciente'])
            _logger.info("Mensaje final generado.")

            return {
                'success': True,
                'finalizado': True,
                'modo': 'COMPLETADO',
                'texto_para_usuario': mensaje_final,
                'text': mensaje_final,
                'lead_resultado': lead_resultado,
                'session_id': session_id,
                'conversation_id': conversation_id,
                'account_id': account_id
            }
    # ==================================================================
    #  MÉTODOS ORIGINALES (SIN MODIFICACIONES, SE MANTIENEN IGUAL)
    # ==================================================================
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
        """
        try:
            if not isinstance(estado_data, dict):
                raise ValidationError(_("Los datos del estado deben ser un diccionario"))
            
            registro = self.search([('session_id', '=', session_id)], limit=1)
            
            if registro:
                estado_actual = registro.estado or {}
                
                def merge_dicts(dict1, dict2):
                    result = dict1.copy()
                    for key, value in dict2.items():
                        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                            result[key] = merge_dicts(result[key], value)
                        else:
                            result[key] = value
                    return result
                
                nuevo_estado = merge_dicts(estado_actual, estado_data)
                
                if 'timestamp' in estado_data:
                    nuevo_estado['timestamp'] = estado_data['timestamp']
                elif 'timestamp' not in nuevo_estado:
                    nuevo_estado['timestamp'] = fields.Datetime.now().isoformat()
                
                campos_requeridos = ['modo', 'paso', 'datos_paciente', 'timestamp']
                for campo in campos_requeridos:
                    if campo not in nuevo_estado:
                        if campo == 'modo':
                            nuevo_estado[campo] = estado_data.get('modo', 'INICIO')
                        elif campo == 'paso':
                            nuevo_estado[campo] = estado_data.get('paso', 'BIENVENIDA')
                        elif campo == 'datos_paciente':
                            nuevo_estado[campo] = estado_data.get('datos_paciente', {})
                        elif campo == 'timestamp':
                            nuevo_estado[campo] = fields.Datetime.now().isoformat()
                
                registro.estado = nuevo_estado
                message = _("Estado actualizado correctamente")
                action = 'update'
            else:
                nuevo_estado = estado_data.copy()
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
            
            registro._compute_campos_derivados()
            
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

    @api.model
    def _default_estado(self):
        """Valor por defecto para el estado"""
        return {
            "modo": "INICIO",
            "paso": "BIENVENIDA",
            "datos_paciente": {},
            "timestamp": fields.Datetime.now().isoformat()
        }
    
    @api.model
    def consultar_por_session(self, session_id):
        """
        Consulta un registro por su session_id
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
            
            return {
                'success': True,
                'found': True,
                'session_id': registro.session_id,
                'estado': registro.estado,
                'modo': registro.modo,
                'paso': registro.paso,
                "tipo_dato": registro.estado.get('tipo_dato') if registro.estado else None,
                "es_requerido": registro.estado.get('es_requerido') if registro.estado else None,
                "mensaje_prompt": registro.estado.get('mensaje_prompt') if registro.estado else None,
                "nombre_mostrar": registro.estado.get('nombre_mostrar') if registro.estado else None,
                "datos_paciente":  registro.estado.get('datos_paciente') if registro.estado else None
            }
            
        except Exception as e:
            _logger.error(f"Error al consultar estado: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'session_id': session_id
            }
    
    @api.model
    def limpiar_sesiones_antiguas(self, horas=24):
        """
        Elimina registros más antiguos que X horas
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
    
    @api.model
    def create(self, vals):
        if 'session_id' in vals and not vals['session_id']:
            raise ValidationError(_("El session_id no puede estar vacío"))
        return super(SessionState, self).create(vals)
    
    def write(self, vals):
        if 'session_id' in vals:
            for record in self:
                if record.session_id != vals['session_id']:
                    raise ValidationError(
                        _("No se puede modificar el session_id de una sesión existente")
                    )
        return super(SessionState, self).write(vals)
    
    @api.model
    def actualizar_estado_parcial(self, session_id, campos_actualizar):
        """
        Actualiza solo campos específicos del estado sin perder datos existentes
        """
        try:
            registro = self.search([('session_id', '=', session_id)], limit=1)
            
            if not registro:
                return {
                    'success': False,
                    'error': _("No se encontró sesión con ese ID"),
                    'session_id': session_id
                }
            
            estado_actual = registro.estado or {}
            
            for campo, valor in campos_actualizar.items():
                if campo == 'datos_paciente' and isinstance(valor, dict):
                    if 'datos_paciente' not in estado_actual:
                        estado_actual['datos_paciente'] = {}
                    
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
                    estado_actual[campo] = valor
            
            estado_actual['timestamp'] = fields.Datetime.now().isoformat()
            registro.estado = estado_actual
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

    def capturar_lead(self, datos):
        """
        Crea un lead/cita con los datos recolectados durante el flujo.
        datos debe incluir: solicitar_vat, solicitar_phone, solicitar_name, solicitar_birthdate,
        equipo_asignado, plataforma, session_id, conversation_id, account_id, etc.
        Retorna {'success': bool, 'lead_info': dict, 'error': str}
        """
        try:
            _logger.info("Iniciando capturar_lead para sesión %s", datos.get('session_id'))
            # Reutilizar la lógica de ChatBotUtils (similar al controlador existente)
            env = self.env
            # Crear o actualizar contacto
            _logger.info("Actualizando/Creando contacto...")
            partner = ChatBotUtils.update_create_contact(env, {
                'solicitar_vat': datos.get('solicitar_vat', ''),
                'solicitar_phone': datos.get('solicitar_phone', ''),
                'solicitar_name': datos.get('solicitar_name', ''),
                'solicitar_birthdate': datos.get('solicitar_birthdate', '')
            })
            # Configurar UTM y etiquetas
            plataforma = datos.get('plataforma', 'whatsapp')
            medium, source, campaign = ChatBotUtils.setup_utm(env, plataforma)
            tag = ChatBotUtils.get_or_create_bot_tag(env, plataforma)
            teams = ChatBotUtils.get_team_unisa(env)

            equipo_asignado = datos.get('equipo_asignado', 'Agendamiento_Directo')
            mapeo_grupos = {
                'Agendamiento_Directo': 'Grupo Citas',
                'Agendamiento_Otra_Consulta': 'Grupo Citas',
                'Agendamiento_Precios': 'Grupo Citas',
                'Agendamiento_Tarjeta': 'Grupo Ventas',
                'Agendamiento_Servicios': 'Grupo Ventas'
            }
            nombre_grupo = mapeo_grupos.get(equipo_asignado, 'Grupo Citas')
            team = None
            if teams and nombre_grupo in teams:
                team = teams[nombre_grupo]
            else:
                team = env['crm.team'].search([('name', '=', nombre_grupo)], limit=1)
                if not team:
                    team = env['crm.team'].search([], limit=1)
            # Crear lead
            lead = ChatBotUtils.create_lead(env, datos, partner, team, medium, source, campaign, tag)
            # Asignación round robin
            if team and team.member_ids:
                ChatBotUtils.assign_lead_round_robin(env, lead, team)
            # Manejar imágenes si vienen
            if 'solicitar_foto_vat' in datos or 'solicitar_imagenes_adicionales' in datos:
                validated_images = ChatBotUtils.validate_image_urls(datos)
                datos.update(validated_images)
                ChatBotUtils.handle_images(env, datos, lead, partner)
                
            return {'success': True, 'lead_info': {'lead_id': lead.id, 'cliente_id': partner.id}}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _generar_mensaje_sin_sesion(self, texto_usuario):
        """Genera un mensaje amigable cuando no hay sesión activa."""
        service = self._get_gpt_service()
        try:
            # Usamos el mismo caso de uso de finalización pero personalizado
            resultado = service.generar_mensaje_personalizado(
                contexto="sin_sesion",
                texto_usuario=texto_usuario
            )
            return resultado.get('mensaje', 'No tengo una conversación activa. ¿Quieres comenzar de nuevo?')
        except Exception:
            return "No tengo una conversación activa. ¿Quieres comenzar de nuevo?"

            
    def _detectar_intencion_salida(self, texto_usuario):
        """Usa IA para saber si el usuario quiere salir del flujo."""
        service = self._get_gpt_service()
        try:
            resultado = service.detectar_intencion_salida(texto_usuario)
            return resultado.get('es_salida', False), resultado.get('mensaje', '')
        except Exception as e:
            _logger.error(f"Error detectando intención de salida: {e}")
            # Fallback simple
            texto_lower = texto_usuario.lower()
            palabras_salida = ['salir', 'cancelar', 'terminar', 'menu', 'menú', 'volver']
            es_salida = any(p in texto_lower for p in palabras_salida)
            mensaje = "Entendido. Si deseas continuar más tarde, aquí estaremos. ¡Hasta pronto!" if es_salida else ""
            return es_salida, mensaje

    def _generar_mensaje_finalizacion(self, datos_paciente):
        """Genera un mensaje de éxito amigable al completar el flujo."""
        service = self._get_gpt_service()
        try:
            resultado = service.generar_mensaje_finalizacion(datos_paciente)
            return resultado.get('mensaje_final', '¡Gracias por completar el formulario! Nos pondremos en contacto contigo pronto.')
        except Exception as e:
            _logger.error(f"Error generando mensaje de finalización: {e}")
            return "¡Gracias por completar el formulario! Nos pondremos en contacto contigo a la brevedad. ¡Que tengas un excelente día!"
    
   
    def _generar_mensaje_expirado(self, texto_usuario):
        res = self._get_gpt_service().generar_mensaje_personalizado('expirado', texto_usuario)
        return res.get('mensaje', "Tu sesión ha expirado por inactividad. Por favor, inicia un nuevo proceso.")

    def _generar_mensaje_sin_pasos(self, texto_usuario):
        res = self._get_gpt_service().generar_mensaje_personalizado('sin_pasos', texto_usuario)
        return res.get('mensaje', "El proceso ya estaba completado. ¡Gracias!")
