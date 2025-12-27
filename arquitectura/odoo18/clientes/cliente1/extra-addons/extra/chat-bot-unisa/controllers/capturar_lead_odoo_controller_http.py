from odoo import http
from odoo.http import request, Response
import json
import logging
import re

from .chatbot_utils import ChatBotUtils  # Importar la clase de utilidades

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
        Versión optimizada usando ChatBotUtils
        """
        try:
            _logger.info("=== INICIO BUSQUEDA POR TELEFONO HTTP (OPTIMIZADO) ===")
            
            # 1. Obtener datos de la petición
            http_request = request.httprequest
            content_type = http_request.headers.get('Content-Type', '').lower()
            data = {}
            
            if 'application/json' in content_type:
                try:
                    if http_request.data:
                        raw_data = http_request.get_data(as_text=True)
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
                data = dict(http_request.form)
                if not data:
                    data = dict(http_request.args)
            
            # 2. Extraer teléfono de múltiples campos posibles
            telefono = (data.get('telefono') or data.get('phone') or 
                       data.get('telefono_cliente') or data.get('numero') or '')
            
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
            
            _logger.info("Buscando cliente con teléfono: %s", telefono)
            
            # 3. Obtener entorno con permisos de administrador
            try:
                admin_uid = request.env.ref('base.user_admin').id or 2
            except Exception:
                admin_uid = 2
                
            env = request.env(user=admin_uid)
            
            # 4. Buscar cliente usando método optimizado de ChatBotUtils
            # Preparamos datos para la búsqueda
            search_data = {
                'telefono': telefono,
                # Podemos incluir otros datos si están disponibles
                'cedula': data.get('cedula', ''),
                'nombre_completo': data.get('nombre_completo', '')
            }
            
            # Usar búsqueda inteligente que maneja múltiples formatos de teléfono
            partner = ChatBotUtils.update_create_contact(env, search_data)
            
            # 5. Si encontramos el cliente
            if partner and partner.id and partner.name and partner.name != 'Sin nombre':
                _logger.info("Cliente encontrado: %s (ID: %s)", partner.name, partner.id)
                
                # Obtener información de última cita
                ultima_cita_info = ChatBotUtils.get_ultima_cita(env, partner.id)
                ultima_cita_str = ""
                if ultima_cita_info:
                    ultima_cita_str = f"{ultima_cita_info.get('fecha', '')} - {ultima_cita_info.get('servicio', '')}"
                
                # Formatear fecha de nacimiento si existe
                fecha_nac_formateada = ''
                if partner.birthdate:
                    try:
                        fecha_nac_formateada = partner.birthdate.strftime('%d/%m/%Y')
                    except Exception:
                        fecha_nac_formateada = str(partner.birthdate)
                
                # Construir respuesta
                response_data = {
                    'existe': True,
                    'iniciales': self._get_iniciales(partner.name),
                    'ultima_cita': ultima_cita_str,
                    'cedula': partner.vat or '',
                    'nombre_completo': partner.name or '',
                    'fecha_nacimiento': fecha_nac_formateada,
                    'telefono': partner.mobile or partner.phone or '',
                    'email': partner.email or '',
                    'es_paciente_nuevo': 'no',
                    'id_cliente': partner.id,
                    'pais': partner.country_id.name if partner.country_id else '',
                    'ciudad': partner.city or '',
                    'detalle_ultima_cita': ultima_cita_info or {}
                }
                
                _logger.info("Respuesta para cliente encontrado: %s", json.dumps(response_data, default=str))
                
                return Response(
                    json.dumps(response_data, default=str),
                    content_type='application/json; charset=utf-8',
                    headers=[('Access-Control-Allow-Origin', '*')]
                )
            
            # 6. Si NO encontramos el cliente
            _logger.info("Cliente NO encontrado para teléfono: %s", telefono)
            
            return Response(
                json.dumps({
                    'existe': False,
                    'mensaje': 'Cliente no encontrado',
                    'telefono_buscado': telefono,
                    'sugerencia': 'Puede ser un nuevo cliente o el teléfono no está registrado'
                }),
                content_type='application/json; charset=utf-8',
                headers=[('Access-Control-Allow-Origin', '*')]
            )
            
        except Exception as e:
            _logger.error("ERROR CRÍTICO BUSCANDO POR TELÉFONO: %s", str(e), exc_info=True)
            
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
        """Obtiene las iniciales del nombre (mantenido para compatibilidad)"""
        if not nombre_completo:
            return ''
        
        try:
            partes = nombre_completo.split()
            iniciales = ''.join([parte[0].upper() for parte in partes[:2] if parte])
            return iniciales
        except Exception:
            return nombre_completo[:2].upper() if len(nombre_completo) >= 2 else nombre_completo[0].upper()
    
    @http.route('/chat-bot-unisa/capturar_lead_http',
                auth='public',
                type='http',
                methods=['POST'],
                csrf=False,
                cors='*')
    def capturar_lead_http(self, **kw):
        """
        Crear cita completa usando ChatBotUtils
        Versión optimizada
        """
        try:
            _logger.info("=== INICIO CREACION DE CITA HTTP (OPTIMIZADO) ===")
            
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
                except json.JSONDecodeError as e:
                    return Response(
                        json.dumps({'error': True, 'mensaje': 'JSON inválido'}),
                        status=400,
                        content_type='application/json; charset=utf-8'
                    )
            else:
                data = dict(http_request.form)
                if not data:
                    data = dict(http_request.args)
            
            _logger.info("Datos recibidos para crear cita: %s", json.dumps(data, default=str))
            
            # 2. Validar datos requeridos
            campos_requeridos = ['cedula', 'telefono', 'nombre_completo', 'fecha_nacimiento']
            for campo in campos_requeridos:
                if campo not in data or not data[campo]:
                    return Response(
                        json.dumps({
                            'error': True,
                            'mensaje': f'Campo requerido faltante: {campo}'
                        }),
                        content_type='application/json; charset=utf-8'
                    )
            
            # 3. Obtener entorno con permisos de administrador
            try:
                admin_uid = request.env.ref('base.user_admin').id or 2
            except Exception:
                admin_uid = 2
                
            env = request.env(user=admin_uid)
            
            # 4. Buscar o crear contacto usando ChatBotUtils
            partner = ChatBotUtils.update_create_contact(env, {
                'cedula': data.get('cedula', ''),
                'telefono': data.get('telefono', ''),
                'nombre_completo': data.get('nombre_completo', ''),
                'fecha_nacimiento': data.get('fecha_nacimiento', '')
            })
            
            # 5. Configurar UTM y etiquetas
            plataforma = data.get('plataforma', 'whatsapp')
            medium, source, campaign = ChatBotUtils.setup_utm(env, plataforma)
            tag = ChatBotUtils.get_or_create_bot_tag(env, plataforma)
            team = ChatBotUtils.get_team_unisa(env)
            
            # 6. Crear lead (cita)
            lead = ChatBotUtils.create_lead(env, data, partner, team, medium, source, campaign, tag)
            
            # 7. Asignar lead automáticamente (round robin)
            if team and team.member_ids:
                ChatBotUtils.assign_lead_round_robin(env, lead, team)
            
            # 8. Manejar imágenes adjuntas si existen
            if data.get('foto_cedula_url') or data.get('imagenes_adicionales'):
                ChatBotUtils.handle_images(env, data, lead, partner)
            
            # 9. Generar respuesta para el bot
            respuesta_bot = ChatBotUtils.generate_response(data)
            
            # 10. Retornar respuesta exitosa
            response_data = {
                'existe': True,
                'lead_id': lead.id,
                'cliente_id': partner.id,
                'cliente_nombre': partner.name,
                'telefono': data.get('telefono'),
                'cedula': data.get('cedula'),
                'fecha_preferida': data.get('fecha_preferida', ''),
                'hora_preferida': data.get('hora_preferida', ''),
                'respuesta_para_bot': respuesta_bot,
                'mensaje': 'Cita registrada exitosamente. Un ejecutivo se contactará pronto.'
            }
            
            _logger.info("Cita creada exitosamente: Lead ID %s para cliente %s", lead.id, partner.name)
            
            return Response(
                json.dumps(response_data, default=str),
                content_type='application/json; charset=utf-8',
                headers=[('Access-Control-Allow-Origin', '*')]
            )
            
        except Exception as e:
            _logger.error("ERROR CREANDO CITA: %s", str(e), exc_info=True)
            
            return Response(
                json.dumps({
                    'existe': False,
                    'error': True,
                    'mensaje': 'Error al crear la cita',
                    'detalle': str(e)
                }),
                status=500,
                content_type='application/json; charset=utf-8',
                headers=[('Access-Control-Allow-Origin', '*')]
            )