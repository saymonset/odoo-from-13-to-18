from odoo import api, fields, models


class ChatbotFlujo(models.Model):
    _name = "chatbot.flujo"
    _description = "Flujo de chatbot"

    name = fields.Char(string="Nombre del flujo", required=True)
    company_id = fields.Many2one("res.company", string="Empresa", required=True)
    paso_ids = fields.One2many(
        "chatbot.paso",
        "flujo_id",
        string="Pasos",
        copy=True,
        default=lambda self: self._default_pasos(),
    )
    active = fields.Boolean(default=True)

    def _default_pasos(self):
        """Retorna comandos para crear los pasos por defecto al abrir un nuevo flujo."""
        return [
            (
                0,
                0,
                {
                    "secuencia": 10,
                    "nombre_interno": "solicitar_phone",
                    "nombre_mostrar": "Teléfono",
                    "tipo_dato": "text",
                    "campo_destino": "solicitar_phone",
                    "es_requerido": True,
                    "es_paso_telefono": True,  # Marcar solo el teléfono como especial
                    "mensaje_prompt": "Por favor, ingresa tu número de teléfono:",
                    "mensaje_error": "Número inválido, intenta de nuevo.",
                },
            ),
            (
                0,
                0,
                {
                    "secuencia": 11,
                    "nombre_interno": "solicitar_name",
                    "nombre_mostrar": "Nombre completo",
                    "tipo_dato": "text",
                    "campo_destino": "solicitar_name",
                    "es_requerido": True,
                    "es_paso_telefono": False,
                    "mensaje_prompt": "Por favor, ingresa tu nombre completo:",
                    "mensaje_error": "Nombre inválido, intenta de nuevo.",
                },
            ),
            (
                0,
                0,
                {
                    "secuencia": 12,
                    "nombre_interno": "solicitar_vat",
                    "nombre_mostrar": "Cédula",
                    "tipo_dato": "text",
                    "campo_destino": "solicitar_vat",
                    "es_requerido": True,
                    "es_paso_telefono": False,
                    "mensaje_prompt": "Por favor, ingresa tu número de cédula:",
                    "mensaje_error": "Cédula inválida, intenta de nuevo.",
                },
            ),
            (
                0,
                0,
                {
                    "secuencia": 13,
                    "nombre_interno": "solicitar_birthdate",
                    "nombre_mostrar": "Fecha de nacimiento",
                    "tipo_dato": "date",
                    "campo_destino": "solicitar_birthdate",
                    "es_requerido": True,
                    "es_paso_telefono": False,
                    "mensaje_prompt": "Por favor, ingresa tu fecha de nacimiento (DD/MM/YYYY):",
                    "mensaje_error": "Fecha inválida, intenta de nuevo con formato DD/MM/YYYY.",
                },
            ),
            # Pasos opcionales (secuencia 14 en adelante)
            (
                0,
                0,
                {
                    "secuencia": 14,
                    "nombre_interno": "solicitar_servicio",
                    "nombre_mostrar": "Servicio solicitado",
                    "tipo_dato": "text",
                    "campo_destino": "solicitar_servicio",
                    "es_requerido": False,
                    "es_paso_telefono": False,
                    "mensaje_prompt": "¿Qué servicio deseas?",
                    "mensaje_error": "",
                },
            ),
            (
                0,
                0,
                {
                    "secuencia": 15,
                    "nombre_interno": "solicitar_fecha_preferida",
                    "nombre_mostrar": "Fecha preferida",
                    "tipo_dato": "text",
                    "campo_destino": "solicitar_fecha_preferida",
                    "es_requerido": False,
                    "es_paso_telefono": False,
                    "mensaje_prompt": 'Indica una fecha preferida (DD/MM/YYYY) o escribe "lo antes posible"',
                    "mensaje_error": "Formato de fecha inválido. Usa DD/MM/YYYY.",
                },
            ),
            (
                0,
                0,
                {
                    "secuencia": 16,
                    "nombre_interno": "solicitar_hora_preferida",
                    "nombre_mostrar": "Horario preferido",
                    "tipo_dato": "text",
                    "campo_destino": "solicitar_hora_preferida",
                    "es_requerido": False,
                    "es_paso_telefono": False,
                    "mensaje_prompt": "¿Qué horario prefieres? (mañana, tarde, cualquier hora)",
                    "mensaje_error": "",
                },
            ),
            (
                0,
                0,
                {
                    "secuencia": 17,
                    "nombre_interno": "solicitar_medio_pago",
                    "nombre_mostrar": "Medio de pago",
                    "tipo_dato": "text",
                    "campo_destino": "solicitar_medio_pago",
                    "es_requerido": False,
                    "es_paso_telefono": False,
                    "mensaje_prompt": "¿Cómo piensas pagar? (efectivo, tarjeta, etc.)",
                    "mensaje_error": "",
                },
            ),
            (
                0,
                0,
                {
                    "secuencia": 18,
                    "nombre_interno": "solicitar_es_paciente_nuevo",
                    "nombre_mostrar": "¿Eres paciente nuevo?",
                    "tipo_dato": "text",
                    "campo_destino": "solicitar_es_paciente_nuevo",
                    "es_requerido": False,
                    "es_paso_telefono": False,
                    "mensaje_prompt": "¿Es tu primera consulta? Responde sí o no",
                    "mensaje_error": "Responde sí o no.",
                },
            ),
            (
                0,
                0,
                {
                    "secuencia": 19,
                    "nombre_interno": "solicitar_membresia_interes",
                    "nombre_mostrar": "¿Interés en membresía?",
                    "tipo_dato": "boolean",
                    "campo_destino": "solicitar_membresia_interes",
                    "es_requerido": False,
                    "es_paso_telefono": False,
                    "mensaje_prompt": "¿Te interesa la Tarjeta Salud? (sí/no)",
                    "mensaje_error": "Responde sí o no.",
                },
            ),
            (
                0,
                0,
                {
                    "secuencia": 20,
                    "nombre_interno": "solicitar_foto_vat",
                    "nombre_mostrar": "Foto de cédula",
                    "tipo_dato": "image",  # o 'text' si solo esperas URL
                    "campo_destino": "solicitar_foto_vat",
                    "es_requerido": False,
                    "es_paso_telefono": False,
                    "mensaje_prompt": "Comparte la foto de tu cédula",
                    "mensaje_error": "",
                },
            ),
            (
                0,
                0,
                {
                    "secuencia": 21,
                    "nombre_interno": "solicitar_imagenes_adicionales",
                    "nombre_mostrar": "Imágenes adicionales",
                    "tipo_dato": "image",  # Almacena URLs como JSON string
                    "campo_destino": "solicitar_imagenes_adicionales",
                    "es_requerido": False,
                    "es_paso_telefono": False,
                    "mensaje_prompt": "Comparte imágenes adicionales si lo deseas",
                    "mensaje_error": "",
                },
            ),
        ]

    @api.model_create_multi
    def create(self, vals_list):
        flujos = super().create(vals_list)
        # Solo crear pasos si el flujo no tiene ninguno (por ejemplo, si se creó sin usar el default)
        for flujo in flujos:
            if not flujo.paso_ids:
                Paso = self.env["chatbot.paso"]
                for vals in self._default_pasos():
                    # Los comandos (0, 0, {...}) no sirven directamente aquí; extraemos el dict
                    paso_vals = vals[2].copy()
                    paso_vals["flujo_id"] = flujo.id
                    Paso.create(paso_vals)
        return flujos
