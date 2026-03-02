from odoo import http
from odoo.http import request, Response
import json
import logging
import datetime
import traceback
import uuid
import re
_logger = logging.getLogger(__name__)


class SessionStateController(http.Controller):
    """
    Controlador REST para manejar estados de sesión
    Permite probar el modelo SessionState desde Postman
    """
    
    @http.route('/api/session/guardar',
                auth='public',
                type='http',
                methods=['POST', 'OPTIONS'],
                csrf=False,
                cors='*')
    def guardar_estado(self, **kw):
        """
        Guarda o actualiza el estado de una sesión
        Método: POST
        Content-Type: application/json
        
        Parámetros:
        {
            "session_id": "session_123456",
            "estado": {
                "modo": "AGENDANDO_CITA",
                "paso": "SOLICITAR_TELEFONO",
                "datos_paciente": {
                    "telefono": "+123456789",
                    "nombre": "Juan Pérez"
                },
                "timestamp": "2026-01-20T12:18:04.696Z"
            }
        }
        """
        try:
            # Manejar preflight CORS
            if request.httprequest.method == 'OPTIONS':
                return Response(
                    status=200,
                    headers=[
                        ('Access-Control-Allow-Origin', '*'),
                        ('Access-Control-Allow-Methods', 'POST, OPTIONS, GET'),
                        ('Access-Control-Allow-Headers', 'Content-Type, Authorization'),
                        ('Access-Control-Max-Age', '86400')
                    ]
                )
            
            _logger.info("=== INICIO GUARDAR ESTADO SESIÓN ===")
            
            # 1. Obtener datos de la petición
            http_request = request.httprequest
            content_type = http_request.headers.get('Content-Type', '').lower()
            data = {}
            
            if 'application/json' in content_type:
                try:
                    if http_request.data:
                        raw_data = http_request.get_data(as_text=True)
                        _logger.debug("Datos JSON recibidos: %s", raw_data)
                        if raw_data.strip():
                            data = json.loads(raw_data)
                except json.JSONDecodeError as e:
                    _logger.error("Error decodificando JSON: %s", str(e))
                    return Response(
                        json.dumps({
                            'success': False,
                            'error': 'Formato JSON inválido',
                            'detalle': str(e),
                            'timestamp': datetime.datetime.now().isoformat()
                        }),
                        status=400,
                        content_type='application/json; charset=utf-8',
                        headers=[('Access-Control-Allow-Origin', '*')]
                    )
            else:
                # Si no es JSON, intentar con form data
                data = dict(http_request.form)
                if not data:
                    data = dict(http_request.args)
                _logger.debug("Datos form recibidos: %s", data)
            
            _logger.info("Datos procesados para guardar estado: %s", json.dumps(data, default=str))
            
            # 2. Validar datos requeridos
            if 'session_id' not in data or not data['session_id']:
                return Response(
                    json.dumps({
                        'success': False,
                        'error': 'El campo "session_id" es requerido',
                        'timestamp': datetime.datetime.now().isoformat()
                    }),
                    status=400,
                    content_type='application/json; charset=utf-8',
                    headers=[('Access-Control-Allow-Origin', '*')]
                )
            
            if 'estado' not in data:
                return Response(
                    json.dumps({
                        'success': False,
                        'error': 'El campo "estado" es requerido',
                        'timestamp': datetime.datetime.now().isoformat()
                    }),
                    status=400,
                    content_type='application/json; charset=utf-8',
                    headers=[('Access-Control-Allow-Origin', '*')]
                )
            
            # 3. Validar que estado sea un diccionario
            if not isinstance(data['estado'], dict):
                return Response(
                    json.dumps({
                        'success': False,
                        'error': 'El campo "estado" debe ser un objeto JSON',
                        'timestamp': datetime.datetime.now().isoformat()
                    }),
                    status=400,
                    content_type='application/json; charset=utf-8',
                    headers=[('Access-Control-Allow-Origin', '*')]
                )
            
            # 4. Asegurar que el estado tenga timestamp
            estado_data = data['estado'].copy()
            if 'timestamp' not in estado_data:
                estado_data['timestamp'] = datetime.datetime.now().isoformat()
            
            # 5. Obtener entorno con permisos
            try:
                # Usar usuario administrador o crear un usuario específico para API
                admin_uid = request.env.ref('base.user_admin').id or 2
            except Exception:
                admin_uid = 2
            
            # Usar sudo para evitar problemas de permisos en pruebas
            env = request.env(user=admin_uid)
            
            # 6. Llamar al método del modelo
            resultado = env['session.state'].sudo().guardar_estado(
                session_id=data['session_id'],
                estado_data=estado_data
            )
            
            # 7. Preparar respuesta
            status_code = 200 if resultado.get('success') else 500
            
            # Agregar información adicional a la respuesta
            respuesta = {
                **resultado,
                'endpoint': '/api/session/guardar',
                'method': 'POST',
                'timestamp': datetime.datetime.now().isoformat(),
                'request_id': str(uuid.uuid4())
            }
            
            _logger.info("Respuesta guardar estado: %s", json.dumps(respuesta, default=str))
            
            return Response(
                json.dumps(respuesta, default=str),
                status=status_code,
                content_type='application/json; charset=utf-8',
                headers=[('Access-Control-Allow-Origin', '*')]
            )
            
        except Exception as e:
            _logger.error("ERROR CRÍTICO GUARDANDO ESTADO: %s", str(e), exc_info=True)
            
            return Response(
                json.dumps({
                    'success': False,
                    'error': 'Error interno del servidor',
                    'detalle': str(e),
                    'traceback': traceback.format_exc() if _logger.isEnabledFor(logging.DEBUG) else None,
                    'timestamp': datetime.datetime.now().isoformat(),
                    'endpoint': '/api/session/guardar'
                }),
                status=500,
                content_type='application/json; charset=utf-8',
                headers=[('Access-Control-Allow-Origin', '*')]
            )
    
    @http.route('/api/session/consultar',
            auth='public',
            type='http',
            methods=['POST', 'GET', 'OPTIONS'],
            csrf=False,
            cors='*')
    def consultar_estado(self, **kw):
        """
        Consulta el estado de una sesión
        Métodos: POST (JSON) o GET (query params)
        
        POST (JSON):
        {
            "session_id": "session_123456"
        }
        
        GET (query params):
        /api/session/consultar?session_id=session_123456
        """
        try:
            # Manejar preflight CORS
            if request.httprequest.method == 'OPTIONS':
                return Response(
                    status=200,
                    headers=[
                        ('Access-Control-Allow-Origin', '*'),
                        ('Access-Control-Allow-Methods', 'POST, GET, OPTIONS'),
                        ('Access-Control-Allow-Headers', 'Content-Type, Authorization'),
                        ('Access-Control-Max-Age', '86400')
                    ]
                )
            
            _logger.info("=== INICIO CONSULTAR ESTADO SESIÓN ===")
            
            session_id = None
            http_request = request.httprequest
            
            # 1. Determinar método y obtener session_id
            if http_request.method == 'POST':
                content_type = http_request.headers.get('Content-Type', '').lower()
                
                if 'application/json' in content_type:
                    try:
                        if http_request.data:
                            raw_data = http_request.get_data(as_text=True)
                            data = json.loads(raw_data) if raw_data.strip() else {}
                            session_id = data.get('session_id')
                    except json.JSONDecodeError:
                        # Si falla JSON, intentar con form data
                        data = dict(http_request.form)
                        session_id = data.get('session_id')
                else:
                    data = dict(http_request.form)
                    session_id = data.get('session_id')
            
            elif http_request.method == 'GET':
                # Obtener de query parameters
                session_id = http_request.args.get('session_id')
            
            # 2. Validar session_id
            if not session_id:
                return Response(
                    json.dumps({
                        'success': False,
                        'error': 'El parámetro "session_id" es requerido',
                        'sugerencia': 'Envíalo como JSON en POST o como query param en GET',
                        'timestamp': datetime.datetime.now().isoformat()
                    }),
                    status=400,
                    content_type='application/json; charset=utf-8',
                    headers=[('Access-Control-Allow-Origin', '*')]
                )
            
            _logger.info("Consultando estado para session_id: %s", session_id)
            
            # 3. Obtener entorno con permisos
            try:
                admin_uid = request.env.ref('base.user_admin').id or 2
            except Exception:
                admin_uid = 2
            
            env = request.env(user=admin_uid)
            
            # 4. INTELIGENTE: Crear variaciones del session_id para buscar
            original_session_id = str(session_id).strip()
            session_id_variations = [original_session_id]
            
            # Si parece un número (dígitos con o sin +)
            if original_session_id.replace('+', '').replace(' ', '').isdigit():
                # Remover todos los caracteres no numéricos
                numbers_only = re.sub(r'\D', '', original_session_id)
                
                # Agregar variaciones:
                # 1. Números solamente
                if numbers_only and numbers_only not in session_id_variations:
                    session_id_variations.append(numbers_only)
                
                # 2. Con + al principio (si no lo tiene)
                if not original_session_id.startswith('+') and numbers_only:
                    with_plus = '+' + numbers_only
                    if with_plus not in session_id_variations:
                        session_id_variations.append(with_plus)
                
                # 3. Sin + (si lo tiene)
                if original_session_id.startswith('+'):
                    without_plus = original_session_id[1:]
                    if without_plus not in session_id_variations:
                        session_id_variations.append(without_plus)
                
                # 4. Últimos 10 dígitos (si es un número largo)
                if len(numbers_only) > 10:
                    last_10 = numbers_only[-10:]
                    if last_10 not in session_id_variations:
                        session_id_variations.append(last_10)
            
            _logger.info("Variaciones a buscar: %s", session_id_variations)
            
            # 5. Buscar en todas las variaciones
            resultado = None
            matched_variation = None
            
            for variation in session_id_variations:
                _logger.info("Buscando con variación: %s", variation)
                temp_result = env['session.state'].sudo().consultar_por_session(
                    session_id=variation
                )
                
                if temp_result.get('found', False):
                    resultado = temp_result
                    matched_variation = variation
                    _logger.info("Encontrado con variación: %s", variation)
                    break
            
            # 6. Preparar respuesta
            if not resultado or not resultado.get('found', False):
                respuesta = [
                    {
                        "success": True,
                        "found": False,
                        "session_id": original_session_id,
                        "variations_tried": session_id_variations,
                        "matched_variation": None,
                        "estado": {
                            "modo": None,
                            "paso": None,
                            "datos_paciente": {},
                            "timestamp": None
                        },
                        "modo": None,
                        "paso": None,
                        "timestamp_estado": None,
                        "create_date": None,
                        "write_date": None,
                        "record_id": None,
                        "endpoint": '/api/session/consultar',
                        "method": http_request.method,
                        "timestamp": datetime.datetime.now().isoformat(),
                        "request_id": str(uuid.uuid4())
                    }
                ]
                status_code = 200
            else:
                # Si se encontró, agregar información sobre la variación encontrada
                if isinstance(resultado, dict):
                    respuesta = [{
                        **resultado,
                        "original_session_id": original_session_id,
                        "matched_variation": matched_variation,
                        "endpoint": '/api/session/consultar',
                        "method": http_request.method,
                        "timestamp": datetime.datetime.now().isoformat(),
                        "request_id": str(uuid.uuid4())
                    }]
                else:
                    respuesta = resultado
                status_code = 200
            
            _logger.info("Respuesta consultar estado: %s", json.dumps(respuesta, default=str))
            
            return Response(
                json.dumps(respuesta, default=str),
                status=status_code,
                content_type='application/json; charset=utf-8',
                headers=[('Access-Control-Allow-Origin', '*')]
            )
            
        except Exception as e:
            _logger.error("ERROR CRÍTICO CONSULTANDO ESTADO: %s", str(e), exc_info=True)
            
            return Response(
                json.dumps({
                    'success': False,
                    'error': 'Error interno del servidor',
                    'detalle': str(e),
                    'timestamp': datetime.datetime.now().isoformat(),
                    'endpoint': '/api/session/consultar'
                }),
                status=500,
                content_type='application/json; charset=utf-8',
                headers=[('Access-Control-Allow-Origin', '*')]
            )

    @http.route('/api/session/listar',
                auth='public',
                type='http',
                methods=['GET', 'OPTIONS'],
                csrf=False,
                cors='*')
    def listar_sesiones(self, **kw):
        """
        Lista todas las sesiones (con paginación)
        Parámetros GET opcionales:
        - limit: número máximo de registros (default: 50)
        - offset: desplazamiento para paginación (default: 0)
        - modo: filtrar por modo
        - paso: filtrar por paso
        - activas: true/false para filtrar por fecha
        """
        try:
            # Manejar preflight CORS
            if request.httprequest.method == 'OPTIONS':
                return Response(
                    status=200,
                    headers=[
                        ('Access-Control-Allow-Origin', '*'),
                        ('Access-Control-Allow-Methods', 'GET, OPTIONS'),
                        ('Access-Control-Allow-Headers', 'Content-Type, Authorization'),
                        ('Access-Control-Max-Age', '86400')
                    ]
                )
            
            _logger.info("=== INICIO LISTAR SESIONES ===")
            
            # 1. Obtener parámetros
            args = request.httprequest.args
            limit = int(args.get('limit', 50))
            offset = int(args.get('offset', 0))
            modo = args.get('modo')
            paso = args.get('paso')
            activas = args.get('activas')
            
            # 2. Obtener entorno con permisos
            try:
                admin_uid = request.env.ref('base.user_admin').id or 2
            except Exception:
                admin_uid = 2
            
            env = request.env(user=admin_uid)
            
            # 3. Construir dominio de búsqueda
            dominio = []
            
            if modo:
                dominio.append(('modo', 'ilike', modo))
            
            if paso:
                dominio.append(('paso', 'ilike', paso))
            
            if activas and activas.lower() == 'true':
                # Últimas 24 horas
                fecha_limite = datetime.datetime.now() - datetime.timedelta(hours=24)
                dominio.append(('create_date', '>=', fecha_limite))
            
            # 4. Buscar registros
            sesiones = env['session.state'].sudo().search(
                dominio,
                limit=limit,
                offset=offset,
                order='create_date desc'
            )
            
            # 5. Contar total
            total = env['session.state'].sudo().search_count(dominio)
            
            # 6. Preparar respuesta
            datos_sesiones = []
            for sesion in sesiones:
                datos_sesiones.append({
                    'session_id': sesion.session_id,
                    'modo': sesion.modo,
                    'paso': sesion.paso,
                    'timestamp_estado': sesion.timestamp_estado.isoformat() if sesion.timestamp_estado else None,
                    'create_date': sesion.create_date.isoformat() if sesion.create_date else None,
                    'write_date': sesion.write_date.isoformat() if sesion.write_date else None,
                    'record_id': sesion.id,
                    'estado': sesion.estado
                })
            
            respuesta = {
                'success': True,
                'total': total,
                'limit': limit,
                'offset': offset,
                'sesiones': datos_sesiones,
                'endpoint': '/api/session/listar',
                'timestamp': datetime.datetime.now().isoformat(),
                'request_id': str(uuid.uuid4())
            }
            
            _logger.info("Listadas %d sesiones de %d totales", len(datos_sesiones), total)
            
            return Response(
                json.dumps(respuesta, default=str),
                content_type='application/json; charset=utf-8',
                headers=[('Access-Control-Allow-Origin', '*')]
            )
            
        except Exception as e:
            _logger.error("ERROR LISTANDO SESIONES: %s", str(e), exc_info=True)
            
            return Response(
                json.dumps({
                    'success': False,
                    'error': 'Error interno del servidor',
                    'detalle': str(e),
                    'timestamp': datetime.datetime.now().isoformat(),
                    'endpoint': '/api/session/listar'
                }),
                status=500,
                content_type='application/json; charset=utf-8',
                headers=[('Access-Control-Allow-Origin', '*')]
            )
    
    @http.route('/api/session/eliminar',
                auth='public',
                type='http',
                methods=['POST', 'DELETE', 'OPTIONS'],
                csrf=False,
                cors='*')
    def eliminar_sesion(self, **kw):
        """
        Elimina una sesión por session_id
        Métodos: POST, DELETE
        Content-Type: application/json
        
        Parámetros:
        {
            "session_id": "session_123456"
        }
        """
        try:
            # Manejar preflight CORS
            if request.httprequest.method == 'OPTIONS':
                return Response(
                    status=200,
                    headers=[
                        ('Access-Control-Allow-Origin', '*'),
                        ('Access-Control-Allow-Methods', 'POST, DELETE, OPTIONS'),
                        ('Access-Control-Allow-Headers', 'Content-Type, Authorization'),
                        ('Access-Control-Max-Age', '86400')
                    ]
                )
            
            _logger.info("=== INICIO ELIMINAR SESIÓN ===")
            
            # 1. Obtener datos
            http_request = request.httprequest
            content_type = http_request.headers.get('Content-Type', '').lower()
            data = {}
            
            if 'application/json' in content_type:
                try:
                    if http_request.data:
                        raw_data = http_request.get_data(as_text=True)
                        if raw_data.strip():
                            data = json.loads(raw_data)
                except json.JSONDecodeError:
                    # Si falla JSON, intentar con form data
                    data = dict(http_request.form)
            else:
                data = dict(http_request.form)
                if not data:
                    data = dict(http_request.args)
            
            # 2. Validar session_id
            session_id = data.get('session_id')
            if not session_id:
                return Response(
                    json.dumps({
                        'success': False,
                        'error': 'El campo "session_id" es requerido',
                        'timestamp': datetime.datetime.now().isoformat()
                    }),
                    status=400,
                    content_type='application/json; charset=utf-8',
                    headers=[('Access-Control-Allow-Origin', '*')]
                )
            
            _logger.info("Eliminando sesión: %s", session_id)
            
            # 3. Obtener entorno con permisos
            try:
                admin_uid = request.env.ref('base.user_admin').id or 2
            except Exception:
                admin_uid = 2
            
            env = request.env(user=admin_uid)
            
            # 4. Buscar y eliminar
            sesion = env['session.state'].sudo().search([
                ('session_id', '=', session_id)
            ], limit=1)
            
            if not sesion:
                return Response(
                    json.dumps({
                        'success': False,
                        'error': f'Sesión no encontrada: {session_id}',
                        'timestamp': datetime.datetime.now().isoformat()
                    }),
                    status=404,
                    content_type='application/json; charset=utf-8',
                    headers=[('Access-Control-Allow-Origin', '*')]
                )
            
            # Guardar información antes de eliminar
            sesion_info = {
                'session_id': sesion.session_id,
                'modo': sesion.modo,
                'paso': sesion.paso,
                'record_id': sesion.id
            }
            
            # Eliminar
            sesion.unlink()
            
            # 5. Preparar respuesta
            respuesta = {
                'success': True,
                'message': f'Sesión eliminada exitosamente',
                'sesion_eliminada': sesion_info,
                'endpoint': '/api/session/eliminar',
                'method': http_request.method,
                'timestamp': datetime.datetime.now().isoformat(),
                'request_id': str(uuid.uuid4())
            }
            
            _logger.info("Sesión eliminada: %s", session_id)
            
            return Response(
                json.dumps(respuesta, default=str),
                content_type='application/json; charset=utf-8',
                headers=[('Access-Control-Allow-Origin', '*')]
            )
            
        except Exception as e:
            _logger.error("ERROR ELIMINANDO SESIÓN: %s", str(e), exc_info=True)
            
            return Response(
                json.dumps({
                    'success': False,
                    'error': 'Error interno del servidor',
                    'detalle': str(e),
                    'timestamp': datetime.datetime.now().isoformat(),
                    'endpoint': '/api/session/eliminar'
                }),
                status=500,
                content_type='application/json; charset=utf-8',
                headers=[('Access-Control-Allow-Origin', '*')]
            )
    
    @http.route('/api/session/limpiar_antiguas',
                auth='public',
                type='http',
                methods=['POST', 'OPTIONS'],
                csrf=False,
                cors='*')
    def limpiar_sesiones_antiguas(self, **kw):
        """
        Limpia sesiones antiguas (más de X horas)
        Parámetros POST opcionales:
        {
            "horas": 24
        }
        """
        try:
            # Manejar preflight CORS
            if request.httprequest.method == 'OPTIONS':
                return Response(
                    status=200,
                    headers=[
                        ('Access-Control-Allow-Origin', '*'),
                        ('Access-Control-Allow-Methods', 'POST, OPTIONS'),
                        ('Access-Control-Allow-Headers', 'Content-Type, Authorization'),
                        ('Access-Control-Max-Age', '86400')
                    ]
                )
            
            _logger.info("=== INICIO LIMPIAR SESIONES ANTIGUAS ===")
            
            # 1. Obtener datos
            http_request = request.httprequest
            content_type = http_request.headers.get('Content-Type', '').lower()
            data = {}
            
            if 'application/json' in content_type:
                try:
                    if http_request.data:
                        raw_data = http_request.get_data(as_text=True)
                        if raw_data.strip():
                            data = json.loads(raw_data)
                except json.JSONDecodeError:
                    data = dict(http_request.form)
            else:
                data = dict(http_request.form)
                if not data:
                    data = dict(http_request.args)
            
            # 2. Obtener horas (default: 24)
            horas = int(data.get('horas', 24))
            
            _logger.info("Limpiando sesiones con más de %d horas", horas)
            
            # 3. Obtener entorno con permisos
            try:
                admin_uid = request.env.ref('base.user_admin').id or 2
            except Exception:
                admin_uid = 2
            
            env = request.env(user=admin_uid)
            
            # 4. Llamar al método del modelo
            resultado = env['session.state'].sudo().limpiar_sesiones_antiguas(horas=horas)
            
            # 5. Preparar respuesta
            respuesta = {
                **resultado,
                'endpoint': '/api/session/limpiar_antiguas',
                'timestamp': datetime.datetime.now().isoformat(),
                'request_id': str(uuid.uuid4())
            }
            
            _logger.info("Resultado limpieza: %s", json.dumps(respuesta, default=str))
            
            return Response(
                json.dumps(respuesta, default=str),
                content_type='application/json; charset=utf-8',
                headers=[('Access-Control-Allow-Origin', '*')]
            )
            
        except Exception as e:
            _logger.error("ERROR LIMPIANDO SESIONES: %s", str(e), exc_info=True)
            
            return Response(
                json.dumps({
                    'success': False,
                    'error': 'Error interno del servidor',
                    'detalle': str(e),
                    'timestamp': datetime.datetime.now().isoformat(),
                    'endpoint': '/api/session/limpiar_antiguas'
                }),
                status=500,
                content_type='application/json; charset=utf-8',
                headers=[('Access-Control-Allow-Origin', '*')]
            )
    
    @http.route('/api/session/health',
                auth='public',
                type='http',
                methods=['GET', 'OPTIONS'],
                csrf=False,
                cors='*')
    def health_check(self, **kw):
        """
        Endpoint de salud/verificación del servicio
        """
        try:
            # Manejar preflight CORS
            if request.httprequest.method == 'OPTIONS':
                return Response(
                    status=200,
                    headers=[
                        ('Access-Control-Allow-Origin', '*'),
                        ('Access-Control-Allow-Methods', 'GET, OPTIONS'),
                        ('Access-Control-Allow-Headers', 'Content-Type, Authorization'),
                        ('Access-Control-Max-Age', '86400')
                    ]
                )
            
            # Obtener entorno
            try:
                admin_uid = request.env.ref('base.user_admin').id or 2
            except Exception:
                admin_uid = 2
            
            env = request.env(user=admin_uid)
            
            # Contar sesiones
            total_sesiones = env['session.state'].sudo().search_count([])
            
            # Verificar que el modelo existe y es accesible
            modelo_accesible = True
            try:
                test_session = env['session.state'].sudo().search([], limit=1)
                modelo_accesible = True
            except Exception:
                modelo_accesible = False
            
            respuesta = {
                'status': 'healthy',
                'service': 'session_state_api',
                'modelo_accesible': modelo_accesible,
                'total_sesiones': total_sesiones,
                'timestamp': datetime.datetime.now().isoformat(),
                'version': '1.0.0',
                'endpoints': {
                    'guardar': '/api/session/guardar',
                    'consultar': '/api/session/consultar',
                    'listar': '/api/session/listar',
                    'eliminar': '/api/session/eliminar',
                    'limpiar': '/api/session/limpiar_antiguas',
                    'health': '/api/session/health'
                }
            }
            
            return Response(
                json.dumps(respuesta, default=str),
                content_type='application/json; charset=utf-8',
                headers=[('Access-Control-Allow-Origin', '*')]
            )
            
        except Exception as e:
            _logger.error("ERROR EN HEALTH CHECK: %s", str(e))
            
            return Response(
                json.dumps({
                    'status': 'unhealthy',
                    'error': str(e),
                    'timestamp': datetime.datetime.now().isoformat()
                }),
                status=500,
                content_type='application/json; charset=utf-8',
                headers=[('Access-Control-Allow-Origin', '*')]
            )
