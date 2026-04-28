from odoo import http
from odoo.http import request, Response
import json
import logging
import re
from datetime import datetime

from .chatbot_utils import ChatBotUtils  # Importar la clase de utilidades

_logger = logging.getLogger(__name__)


class ChatBotController(http.Controller):
    
    @http.route('/chat_bot_integra/buscar_por_telefono_http',
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
            telefono = (data.get('solicitar_phone') or '')
            
            if not telefono:
                _logger.warning("No se proporcionó teléfono en la petición")
                return Response(
                    json.dumps({
                        'existe': False,
                        'error': True,
                        'mensaje': 'Parámetro "solicitar_phone" es requerido'
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
                'telefono': telefono
            }
            
            # Usar búsqueda inteligente que maneja múltiples formatos de teléfono
            partner = ChatBotUtils.search_contact(env, search_data)
            
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
                    'mensaje': f"✅ **INFORMACIÓN ENCONTRADA**\n\n"
                         f"👤 **Datos del paciente:**\n"
                         f"• Nombre: {partner.name}\n"
                         f"• Cédula: {partner.vat or 'No registrada'}\n"
                         f"• Teléfono: {partner.phone}\n",
                    'ultima_cita': ultima_cita_str,
                    'cedula': partner.vat or '',
                    'nombre_completo': partner.name or '',
                    'fecha_nacimiento': fecha_nac_formateada,
                    'telefono': partner.phone or '',
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
            
            mensaje = "❌ **NO ENCONTRAMOS TU REGISTRO**\n\n"
            mensaje += "No encontramos información con ese número de teléfono.\n\n"
            mensaje += "📋 **Por favor, ingresa tu cédula (solo números):**\n\n"
            mensaje += "Ejemplo: 12345678"
            
            return Response(
                json.dumps({
                    'existe': False,
                    'mensaje': mensaje,
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
    
    @http.route('/chat_bot_integra/capturar_lead_http',
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
            
            # 🔍 LOG DETALLADO DE TODOS LOS DATOS
            _logger.info("=== DATOS COMPLETOS RECIBIDOS ===")
            for key, value in data.items():
                _logger.info("🔑 %s: %s", key, value)
            
            # Verificar específicamente imágenes
            _logger.info("=== VERIFICACIÓN DE IMÁGENES ===")
            _logger.info("solicitar_foto_vat existe? %s", 'solicitar_foto_vat' in data)
            if 'solicitar_foto_vat' in data:
                _logger.info("Valor de solicitar_foto_vat: %s", data.get('solicitar_foto_vat'))
                _logger.info("Es URL válida? %s", bool(re.match(r'^https?://', str(data.get('solicitar_foto_vat', '')))))
            
            _logger.info("solicitar_imagenes_adicionales existe? %s", 'solicitar_imagenes_adicionales' in data)
            if 'solicitar_imagenes_adicionales' in data:
                _logger.info("Valor de solicitar_imagenes_adicionales: %s", data.get('solicitar_imagenes_adicionales'))
            
            # 2. Validar datos requeridos
            campos_requeridos = ['solicitar_vat', 'solicitar_phone', 'solicitar_name', 'solicitar_birthdate']
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
                'solicitar_vat': data.get('solicitar_vat', ''),
                'solicitar_phone': data.get('solicitar_phone', ''),
                'solicitar_name': data.get('solicitar_name', ''),
                'solicitar_birthdate': data.get('solicitar_birthdate', '')
            })
            
            # 5. Configurar UTM y etiquetas
            plataforma = data.get('plataforma', 'whatsapp')
            # Todo relacionado con la platforma que se creo
            medium, source, campaign = ChatBotUtils.setup_utm(env, plataforma)
            # Si no existe la etiequeta, se crea.
            tag = ChatBotUtils.get_or_create_bot_tag(env, plataforma)
            # Crea los grupos si no existen
            teams = ChatBotUtils.get_team_unisa(env)
            
            # 6. OBTENER EQUIPO ASIGNADO SEGÚN EL VALOR RECIBIDO (MODIFICADO)
            equipo_asignado = data.get('equipo_asignado', 'Agendamiento_Directo')
            
            # Mapeo de tipos de agendamiento a grupos
            mapeo_grupos = {
                'Agendamiento_Directo': 'Grupo Citas',
                'Agendamiento_Otra_Consulta': 'Grupo Citas',
                'Agendamiento_Precios': 'Grupo Citas',
                'Agendamiento_Tarjeta': 'Grupo Ventas',
                'Agendamiento_Servicios': 'Grupo Ventas'
            }
            
            # Obtener el nombre del grupo según el mapeo
            nombre_grupo = mapeo_grupos.get(equipo_asignado, 'Grupo Citas')  # Default a 'Grupo Citas'
            
            # Buscar el equipo
            team = None
            if teams and nombre_grupo in teams:
                team = teams.get(nombre_grupo)
            else:
                # Buscar directamente en la base de datos
                team = env['crm.team'].search([('name', '=', nombre_grupo)], limit=1)
                if not team:
                    # Fallback: usar cualquier equipo disponible
                    team = env['crm.team'].search([], limit=1)
                    _logger.warning(f"No se encontró el equipo {nombre_grupo}, usando {team.name if team else 'ninguno'}")
            
            _logger.info(f"Equipo asignado: {equipo_asignado} -> Grupo: {nombre_grupo} -> ID: {team.id if team else 'N/A'}")
            
            # 7. Crear lead (cita)
            lead = ChatBotUtils.create_lead(env, data, partner, team, medium, source, campaign, tag)
            
            # 8. Asignar lead automáticamente (round robin)
            if team and team.member_ids:
                ChatBotUtils.assign_lead_round_robin(env, lead, team)
            
            # 9. Manejar imágenes adjuntas si existen
            if 'solicitar_foto_solicitar_vat' in data or 'solicitar_imagenes_adicionales' in data:
                # Validar URLs de imágenes
                validated_images = ChatBotUtils.validate_image_urls(data)
                data.update(validated_images)
                
                # Crear adjuntos
                ChatBotUtils.handle_images(env, data, lead, partner)
                        
            # 10. Generar respuesta para el bot
            # Agrega el ID del lead a la respuesta
            respuesta_bot = ChatBotUtils.generate_response(data) + f"\n\n📝 **Número de referencia:** {lead.id}"

            # 11. ELIMINAR SESSION SI SE PROPORCIONA session_id
            session_id = data.get('session_id')
            if session_id:
                try:
                    _logger.info("Intentando eliminar sesión: %s", session_id)
                    # Buscar y eliminar la sesión
                    # ], limit=1)
                    # 
                    # if session_record:
                    #     # Eliminar la sesión
                    #     session_record.unlink()
                    #     _logger.info("Sesión eliminada exitosamente: %s", session_id)
                except Exception as e:
                    _logger.error("Error al procesar sesión %s: %s", session_id, str(e), exc_info=True)
            
            # 12. Retornar respuesta exitosa
            response_data = {
                'session_id': data.get('session_id'),
                'conversation_id': data.get('conversation_id'),
                'account_id': data.get('account_id'),
                'existe': True,
                'lead_id': lead.id,
                'cliente_id': partner.id,
                'cliente_nombre': partner.name,
                'telefono': data.get('solicitar_phone'),
                'cedula': data.get('solicitar_vat'),
                'fecha_preferida': data.get('solicitar_fecha_preferida', ''),
                'hora_preferida': data.get('solicitar_hora_preferida', ''),
                'respuesta_para_bot': respuesta_bot,
                'text': respuesta_bot,
                'content': respuesta_bot,
                'output': respuesta_bot,
                'mensaje': 'Cita registrada exitosamente. Un ejecutivo se contactará pronto.',
                'session_eliminada': session_id if session_id else None,
                'equipo_asignado': equipo_asignado,
                'grupo_asignado': nombre_grupo
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
    
    