from odoo import http
from odoo.http import request, Response
import json
import logging
import datetime
import traceback
import uuid

_logger = logging.getLogger(__name__)

class InicioAgendarController(http.Controller):

    def _get_flow_steps(self, flow_name):
        """
        Obtiene los pasos de un flujo por su nombre.
        Retorna un dict con la info del flujo y una lista de pasos,
        o None si no se encuentra.
        """
        # Usamos sudo para evitar problemas de permisos (endpoint público)
        flow = request.env['chatbot.flujo'].sudo().search([
            ('name', '=', flow_name),
            ('active', '=', True)
        ], limit=1)
        if not flow:
            return None

        steps = []
        for paso in flow.paso_ids.sorted('secuencia'):
            #Solo los pasos requeridos se envían al iniciar el flujo, los opcionales se manejan dinámicamente según las respuestas del usuario
            if paso.es_requerido:
                steps.append({
                    'id': paso.id,
                    'secuencia': paso.secuencia,
                    'nombre_interno': paso.nombre_interno,
                    'nombre_mostrar': paso.nombre_mostrar,
                    'tipo_dato': paso.tipo_dato,
                    'mensaje_prompt': paso.mensaje_prompt,
                    'mensaje_error': paso.mensaje_error,
                    'es_requerido': paso.es_requerido,
                    'campo_destino': paso.campo_destino,
                    'es_paso_telefono': paso.es_paso_telefono,  
                })

        return {
            'flow_id': flow.id,
            'flow_name': flow.name,
            'company_id': flow.company_id.id if flow.company_id else None,
            'steps': steps,
        }

    @http.route('/chat_bot_integra/inicioagendar',
                auth='public',
                type='http',
                methods=['POST'],
                csrf=False,
                cors='*')
    def inicio_agendar(self, **kw):
        """
        Endpoint para iniciar proceso de agendar.
        Recibe: {"session_id": "...", "conversation_id": "...", "account_id": "...", "name_flow": "...",  "equipo_asignado": "..."}
        Devuelve: {
            "success": true,
            "session_id": "...",
            "conversation_id": "...",
            "account_id": "...",
            "name_flow": "...",
            "flow_info": { ... },   # info del flujo y sus pasos
            "timestamp": "...",
            "request_id": "..."
        }
        """
        try:
            _logger.info("=== INICIO AGENDAR CONTROLLER ===")

            # Obtener datos de la petición
            http_request = request.httprequest
            content_type = http_request.headers.get('Content-Type', '').lower()
            data = {}

            if 'application/json' in content_type:
                try:
                    raw_data = http_request.get_data(as_text=True)
                    _logger.debug("JSON recibido: %s", raw_data)
                    if raw_data.strip():
                        data = json.loads(raw_data)
                except json.JSONDecodeError as e:
                    _logger.error("Error decodificando JSON: %s", e)
                    return Response(
                        json.dumps({
                            'success': False,
                            'error': 'JSON inválido',
                            'detalle': str(e)
                        }),
                        status=400,
                        content_type='application/json; charset=utf-8',
                        headers=[('Access-Control-Allow-Origin', '*')]
                    )
            else:
                data = dict(http_request.form) or dict(http_request.args)
                _logger.debug("Datos form: %s", data)

            # Validar campos requeridos
            session_id = data.get('session_id')
            conversation_id = data.get('conversation_id')
            account_id = data.get('account_id')
            name_flow = data.get('name_flow')
            equipo_asignado = data.get('equipo_asignado')

            if not session_id:
                return Response(
                    json.dumps({
                        'success': False,
                        'error': 'session_id es requerido'
                    }),
                    status=400,
                    content_type='application/json; charset=utf-8',
                    headers=[('Access-Control-Allow-Origin', '*')]
                )
            if not conversation_id:
                return Response(
                    json.dumps({
                        'success': False,
                        'error': 'conversation_id es requerido'
                    }),
                    status=400,
                    content_type='application/json; charset=utf-8',
                    headers=[('Access-Control-Allow-Origin', '*')]
                )
            if not account_id:
                return Response(
                    json.dumps({
                        'success': False,
                        'error': 'account_id es requerido'
                    }),
                    status=400,
                    content_type='application/json; charset=utf-8',
                    headers=[('Access-Control-Allow-Origin', '*')]
                )

            if not name_flow:
                return Response(
                    json.dumps({
                        'success': False,
                        'error': 'name_flow es requerido'
                    }),
                    status=400,
                    content_type='application/json; charset=utf-8',
                    headers=[('Access-Control-Allow-Origin', '*')]
                )

            # Obtener pasos del flujo
            flow_info = self._get_flow_steps(name_flow)
            if flow_info is None:
                return Response(
                    json.dumps({
                        'success': False,
                        'error': f'No se encontró un flujo activo con nombre "{name_flow}"'
                    }),
                    status=404,
                    content_type='application/json; charset=utf-8',
                    headers=[('Access-Control-Allow-Origin', '*')]
                )
                
            steps = flow_info['steps']  
            
            # Inicializar el flujo en la sesión
            env = request.env(user=2)  # admin
            session_state = env['chatbot.session'].sudo()
            session_state.iniciar_flujo(session_id, name_flow, steps, equipo_asignado)  

            
            # Construir respuesta
            respuesta = {
                'success': True,
                'session_id': session_id,
                'conversation_id': conversation_id,
                'account_id': account_id,
                'name_flow': name_flow,
                'steps': steps,
                'timestamp': datetime.datetime.now().isoformat(),
                'request_id': str(uuid.uuid4())
            }

            _logger.info("Respuesta: %s", json.dumps(respuesta, default=str))
            return Response(
                json.dumps(respuesta, default=str),
                status=200,
                content_type='application/json; charset=utf-8',
                headers=[('Access-Control-Allow-Origin', '*')]
            )

        except Exception as e:
            _logger.error("Error en inicio_agendar: %s", e, exc_info=True)
            return Response(
                json.dumps({
                    'success': False,
                    'error': 'Error interno del servidor',
                    'detalle': str(e)
                }),
                status=500,
                content_type='application/json; charset=utf-8',
                headers=[('Access-Control-Allow-Origin', '*')]
            )
            
            
    @http.route('/chat_bot_integra/procesar_paso',
            auth='public',
            type='http',
            methods=['POST', 'OPTIONS'],
            csrf=False,
            cors='*')
    def procesar_paso(self, **kw):
        try:
            if request.httprequest.method == 'OPTIONS':
                return Response(status=200, headers=[
                    ('Access-Control-Allow-Origin', '*'),
                    ('Access-Control-Allow-Methods', 'POST, OPTIONS'),
                    ('Access-Control-Allow-Headers', 'Content-Type'),
                    ('Access-Control-Max-Age', '86400')
                ])

            # Leer JSON del body
            raw_data = request.httprequest.get_data(as_text=True)
            _logger.info("RAW DATA: %s", raw_data)
            data = json.loads(raw_data)

            session_id = data.get('session_id')
            conversation_id = data.get('conversation_id')
            account_id = data.get('account_id')
            valor = data.get('valor') or data.get('text')
            paso = data.get('paso')

            # Validaciones
            if not session_id:
                return Response(json.dumps({'success': False, 'error': 'session_id requerido'}), status=400, content_type='application/json')
            if not conversation_id:
                return Response(json.dumps({'success': False, 'error': 'conversation_id requerido'}), status=400, content_type='application/json')
            if not account_id:
                return Response(json.dumps({'success': False, 'error': 'account_id requerido'}), status=400, content_type='application/json')
            if valor is None:
                return Response(json.dumps({'success': False, 'error': 'Se requiere text o valor'}), status=400, content_type='application/json')

            # Obtener entorno y modelo
            env = request.env(user=2)
            session_model = env['chatbot.session'].sudo()

            # Si no se envió paso, lo obtenemos de la sesión
            if not paso:
                sesion = session_model.search([('session_id', '=', session_id)], limit=1)
                if sesion and sesion.estado:
                    paso = sesion.estado.get('paso')
                if not paso:
                    # Sin paso y sin sesión o sin flujo activo -> MENU_PRINCIPAL
                    return Response(json.dumps({
                        'success': True,
                        'finalizado': False,
                        'modo': 'MENU_PRINCIPAL',
                        'texto_para_usuario': 'No hay un flujo activo. Puedes comenzar un nuevo proceso.',
                        'text': valor,
                        'session_id': session_id,
                        'conversation_id': conversation_id,
                        'account_id': account_id,
                    }), status=200, content_type='application/json', headers=[('Access-Control-Allow-Origin', '*')])

            # Llamar al método del modelo
            resultado = session_model.procesar_paso(
                session_id=session_id,
                valor=valor,
                paso=paso,
                conversation_id=conversation_id,
                account_id=account_id
            )

            return Response(
                json.dumps(resultado, default=str),
                status=200,
                content_type='application/json',
                headers=[('Access-Control-Allow-Origin', '*')]
            )

        except Exception as e:
            _logger.error("Error en procesar_paso: %s", e, exc_info=True)
            return Response(
                json.dumps({'success': False, 'error': str(e)}),
                status=500,
                content_type='application/json',
                headers=[('Access-Control-Allow-Origin', '*')]
            )