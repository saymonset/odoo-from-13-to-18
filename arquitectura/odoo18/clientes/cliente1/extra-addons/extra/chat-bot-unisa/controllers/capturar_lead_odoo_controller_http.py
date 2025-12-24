from odoo import http
from odoo.http import request, Response
import json
import logging
import re

_logger = logging.getLogger(__name__)


class ChatBotController(http.Controller):
    
    @http.route('/chat-bot-unisa/buscar_por_telefono_http',
                auth='public',
                type='http',
                methods=['POST'],
                csrf=False,
                cors='*')
    def buscar_por_telefono_http(self, **kw):
        """
        Búsqueda rápida solo por teléfono para iniciar conversación
        Versión HTTP estándar (no JSON-RPC 2) - Compatible con cualquier país
        """
        try:
            # Log de inicio
            _logger.info("=== INICIO BUSQUEDA POR TELEFONO HTTP (INTERNACIONAL) ===")
            
            # 1. Obtener el contenido de la petición HTTP
            http_request = request.httprequest
            
            # 2. Verificar el Content-Type
            content_type = http_request.headers.get('Content-Type', '').lower()
            
            # 3. Obtener datos según el Content-Type
            data = {}
            
            if 'application/json' in content_type:
                # Si es JSON, leer y parsear el body
                try:
                    if http_request.data:
                        raw_data = http_request.get_data(as_text=True)
                        _logger.debug("Datos JSON raw: %s", raw_data)
                        if raw_data.strip():
                            data = json.loads(raw_data)
                except json.JSONDecodeError as e:
                    _logger.error("Error decodificando JSON: %s", str(e))
                    return Response(
                        json.dumps({
                            'error': True,
                            'mensaje': 'Formato JSON inválido',
                            'detalle': str(e)
                        }),
                        status=400,
                        content_type='application/json; charset=utf-8',
                        headers=[('Access-Control-Allow-Origin', '*')]
                    )
            else:
                # Si no es JSON, intentar con form data o query params
                data = dict(http_request.form)
                if not data:
                    data = dict(http_request.args)
            
            # 4. Log de datos recibidos
            _logger.info("Datos recibidos: %s", json.dumps(data, indent=2, default=str))
            
            # 5. Extraer teléfono
            telefono = data.get('telefono') or data.get('phone') or data.get('telefono_cliente') or data.get('numero') or ''
            
            if not telefono:
                _logger.warning("No se proporcionó teléfono en la petición")
                return Response(
                    json.dumps({
                        'existe': False,
                        'error': True,
                        'mensaje': 'Parámetro "telefono" es requerido'
                    }),
                    content_type='application/json; charset=utf-8',
                    headers=[('Access-Control-Allow-Origin', '*')]
                )
            
            # 6. Obtener usuario administrador
            try:
                admin_uid = request.env.ref('base.user_admin').id
                if not admin_uid:
                    admin_uid = 2
            except Exception:
                admin_uid = 2
            
            _logger.debug("Usando usuario admin con ID: %s", admin_uid)
            
            # 7. Crear entorno con permisos de administrador
            env = request.env(user=admin_uid)
            
            # 8. Limpiar y formatear teléfono - VERSIÓN GENÉRICA PARA CUALQUIER PAÍS
            # Extraer solo dígitos
            phone_digits = re.sub(r'\D', '', str(telefono))
            
            # Estrategia de búsqueda flexible para cualquier país:
            # 1. Intentar con el número completo
            # 2. Si no se encuentra, intentar variaciones comunes
            
            _logger.info("Teléfono original: %s, Dígitos extraídos: %s", telefono, phone_digits)
            
            if not phone_digits:
                _logger.warning("No se encontraron dígitos en el teléfono")
                return Response(
                    json.dumps({'existe': False}),
                    content_type='application/json; charset=utf-8',
                    headers=[('Access-Control-Allow-Origin', '*')]
                )
            
            # 9. Búsqueda flexible en múltiples formatos
            partner = None
            
            # Lista de posibles formatos para buscar (de más específico a más general)
            search_patterns = []
            
            # Patrón 1: Número completo con todos los dígitos
            search_patterns.append(phone_digits)
            
            # Patrón 2: Si el número es muy largo (>10), intentar con últimos 10 dígitos
            # (muchos países tienen números de 10 dígitos para móviles)
            if len(phone_digits) > 10:
                search_patterns.append(phone_digits[-10:])
            
            # Patrón 3: Intentar sin código de país si parece tenerlo
            # Detectar código de país común (1 a 3 dígitos al inicio)
            if len(phone_digits) > 10:
                # Intentar quitar 1, 2 o 3 dígitos del inicio (posible código de país)
                for country_code_length in [3, 2, 1]:
                    if len(phone_digits) > country_code_length:
                        possible_local_number = phone_digits[country_code_length:]
                        # Solo agregar si el número resultante tiene al menos 8 dígitos
                        if len(possible_local_number) >= 8:
                            search_patterns.append(possible_local_number)
            
            # Patrón 4: Si tiene 11 dígitos y comienza con 0 (común en algunos países)
            if len(phone_digits) == 11 and phone_digits.startswith('0'):
                search_patterns.append(phone_digits[1:])
            
            # Patrón 5: Intentar con últimos 9 dígitos (para países como España)
            if len(phone_digits) >= 9:
                search_patterns.append(phone_digits[-9:])
            
            # Eliminar duplicados manteniendo el orden
            unique_patterns = []
            seen = set()
            for pattern in search_patterns:
                if pattern not in seen:
                    seen.add(pattern)
                    unique_patterns.append(pattern)
            
            _logger.info("Patrones de búsqueda a intentar: %s", unique_patterns)
            
            # 10. Buscar cliente con cada patrón hasta encontrar
            for search_pattern in unique_patterns:
                _logger.debug("Buscando con patrón: %s", search_pattern)
                
                partner = env['res.partner'].search([
                    '|',
                    ('mobile', 'ilike', f'%{search_pattern}%'),
                    ('phone', 'ilike', f'%{search_pattern}%'),
                    ('active', '=', True)
                ], limit=1)
                
                if partner:
                    _logger.info("Cliente encontrado con patrón: %s", search_pattern)
                    break
            
            # 11. Si encontramos el cliente
            if partner:
                _logger.info("Cliente encontrado: %s (ID: %s)", partner.name, partner.id)
                
                # Formatear fecha de nacimiento para el bot (dd/mm/yyyy)
                fecha_nac_formateada = ''
                if partner.birthdate:
                    try:
                        fecha_nac_formateada = partner.birthdate.strftime('%d/%m/%Y')
                    except Exception:
                        fecha_nac_formateada = str(partner.birthdate)
                
                # Obtener última cita
                ultima_cita = self._get_ultima_cita(env, partner.id)
                
                # Determinar teléfono principal a mostrar
                telefono_mostrar = partner.mobile or partner.phone or ''
                
                # Construir respuesta
                response_data = {
                    'existe': True,
                    'iniciales': self._get_iniciales(partner.name),
                    'ultima_cita': ultima_cita,
                    'cedula': partner.vat or '',
                    'nombre_completo': partner.name or '',
                    'fecha_nacimiento': fecha_nac_formateada,
                    'telefono': telefono_mostrar,
                    'email': partner.email or '',
                    'es_paciente_nuevo': 'no',
                    'id_cliente': partner.id,
                    'pais': partner.country_id.name if partner.country_id else '',
                    'ciudad': partner.city or ''
                }
                
                _logger.info("Respuesta para cliente encontrado: %s", json.dumps(response_data, default=str))
                
                return Response(
                    json.dumps(response_data, default=str),
                    content_type='application/json; charset=utf-8',
                    headers=[('Access-Control-Allow-Origin', '*')]
                )
            
            # 12. Si NO encontramos el cliente
            _logger.info("Cliente NO encontrado para teléfono: %s (patrones intentados: %s)", 
                        phone_digits, len(unique_patterns))
            
            return Response(
                json.dumps({
                    'existe': False,
                    'mensaje': 'Cliente no encontrado',
                    'telefono_buscado': telefono,
                    'digitos_extraidos': phone_digits
                }),
                content_type='application/json; charset=utf-8',
                headers=[('Access-Control-Allow-Origin', '*')]
            )
            
        except Exception as e:
            _logger.error("ERROR CRÍTICO BUSCANDO POR TELÉFONO", exc_info=True)
            
            return Response(
                json.dumps({
                    'existe': False,
                    'error': True,
                    'mensaje': 'Error interno del servidor',
                    'tipo_error': type(e).__name__,
                    'detalle': str(e) if _logger.isEnabledFor(logging.DEBUG) else ''
                }),
                status=500,
                content_type='application/json; charset=utf-8',
                headers=[('Access-Control-Allow-Origin', '*')]
            )
    
    def _get_iniciales(self, nombre_completo):
        """Obtiene las iniciales del nombre"""
        if not nombre_completo:
            return ''
        
        try:
            partes = nombre_completo.split()
            iniciales = ''.join([parte[0].upper() for parte in partes[:2] if parte])
            return iniciales
        except Exception:
            return nombre_completo[:2].upper() if len(nombre_completo) >= 2 else nombre_completo[0].upper()
    
    def _get_ultima_cita(self, env, partner_id):
        """
        Método auxiliar para obtener la última cita del paciente
        """
        try:
            # Buscar el modelo de citas (ajusta según tu módulo)
            # Asumiendo que usas calendar.event o un módulo personalizado
            modelos_cita = ['calendar.event', 'medical.appointment', 'cita', 'appointment']
            
            for modelo in modelos_cita:
                if modelo in env:
                    try:
                        ultima_cita = env[modelo].search([
                            ('partner_ids', 'in', [partner_id]),
                            ('start', '!=', False),
                            ('active', '=', True)
                        ], order='start desc', limit=1)
                        
                        if ultima_cita:
                            # Formatear fecha de la última cita
                            fecha_cita = ultima_cita.start
                            if fecha_cita:
                                return fecha_cita.strftime('%d/%m/%Y %H:%M')
                    except Exception as e:
                        _logger.debug("Modelo %s no disponible o error: %s", modelo, str(e))
                        continue
            
            # Si no se encuentra en los modelos comunes, buscar en campos personalizados
            partner = env['res.partner'].browse(partner_id)
            
            # Intentar con campos comunes de fecha de última cita
            campos_fecha = ['ultima_cita', 'last_appointment', 'fecha_ultima_visita', 'last_visit_date']
            
            for campo in campos_fecha:
                if hasattr(partner, campo):
                    fecha = getattr(partner, campo)
                    if fecha:
                        try:
                            return fecha.strftime('%d/%m/%Y %H:%M')
                        except Exception:
                            return str(fecha)
            
            return ''
            
        except Exception as e:
            _logger.error("Error obteniendo última cita: %s", str(e))
            return ''