from odoo import api, fields, models

class ChatbotFlujo(models.Model):
    _name = 'chatbot.flujo'
    _description = 'Flujo de chatbot'

    name = fields.Char(string='Nombre del flujo', required=True)
    company_id = fields.Many2one('res.company', string='Empresa', required=True)
    paso_ids = fields.One2many(
        'chatbot.paso', 'flujo_id', string='Pasos', copy=True,
        default=lambda self: self._default_pasos()
    )
    active = fields.Boolean(default=True)

    def _default_pasos(self):
        """Retorna comandos para crear los pasos por defecto al abrir un nuevo flujo."""
        return [
            (0, 0, {
                'secuencia': 10,
                'nombre_interno': 'solicitar_phone',
                'nombre_mostrar': 'Teléfono',
                'tipo_dato': 'text',
                'campo_destino': 'phone',
                'es_requerido': True,
                'es_paso_telefono': True,  # Marcar solo el teléfono como especial
                'mensaje_prompt': 'Por favor, ingresa tu número de teléfono:',
                'mensaje_error': 'Número inválido, intenta de nuevo.',
            }),
            (0, 0, {
                'secuencia': 11,
                'nombre_interno': 'solicitar_name',
                'nombre_mostrar': 'Nombre completo',
                'tipo_dato': 'text',
                'campo_destino': 'name',
                'es_requerido': True,
                'es_paso_telefono': False,
                'mensaje_prompt': 'Por favor, ingresa tu nombre completo:',
                'mensaje_error': 'Nombre inválido, intenta de nuevo.',
            }),
            (0, 0, {
                'secuencia': 12,
                'nombre_interno': 'solicitar_vat',
                'nombre_mostrar': 'Cédula',
                'tipo_dato': 'text',
                'campo_destino': 'vat',
                'es_requerido': True,
                'es_paso_telefono': False,
                'mensaje_prompt': 'Por favor, ingresa tu número de cédula:',
                'mensaje_error': 'Cédula inválida, intenta de nuevo.',
            }),
        ]

    @api.model_create_multi
    def create(self, vals_list):
        flujos = super().create(vals_list)
        # Solo crear pasos si el flujo no tiene ninguno (por ejemplo, si se creó sin usar el default)
        for flujo in flujos:
            if not flujo.paso_ids:
                Paso = self.env['chatbot.paso']
                for vals in self._default_pasos():
                    # Los comandos (0, 0, {...}) no sirven directamente aquí; extraemos el dict
                    paso_vals = vals[2].copy()
                    paso_vals['flujo_id'] = flujo.id
                    Paso.create(paso_vals)
        return flujos