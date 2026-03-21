from odoo import api, fields, models
class ChatbotPaso(models.Model):
    _name = 'chatbot.paso'
    _description = 'Paso del flujo de chatbot'
    _order = 'flujo_id, secuencia'

    flujo_id = fields.Many2one('chatbot.flujo', string='Flujo', required=True, ondelete='cascade')
    secuencia = fields.Integer(string='Secuencia', default=10)
    nombre_interno = fields.Char(
        string='Nombre interno',
        required=True,
        
        default='solicitar_xxx',
        
        help='Identificador único dentro del flujo (ej: solicitar_xxx)'
    )
    nombre_mostrar = fields.Text(string='Etiqueta para mostrar')
    tipo_dato = fields.Selection([
        ('text', 'Texto'),
        ('integer', 'Número entero'),
        ('float', 'Número decimal'),
        ('date', 'Fecha'),
        ('datetime', 'Fecha y hora'),
        ('image', 'Imagen'),
        ('boolean', 'Sí/No'),
        ('selection', 'Selección (opciones)'),
    ], string='Tipo de dato', required=True, default='text')


    mensaje_prompt = fields.Text(
        string='Mensaje a enviar',
        help='Texto que el chatbot enviará al usuario para solicitar este dato'
    )
    mensaje_error = fields.Text(
        string='Mensaje de error',
        default='Dato inválido, intente nuevamente.'
    )
    es_requerido = fields.Boolean(string='Requerido', default=True)

    # Almacena el nombre del campo en datos_paciente donde se guardará
    campo_destino = fields.Char(
        string='Campo destino',
        required=True,
        help='Nombre de la clave en datos_paciente donde se almacenará el valor'
    )
    
    es_paso_telefono = fields.Boolean(
        string='¿Es el paso de teléfono?',
        default=False,
        help='Marca este paso como el obligatorio de teléfono (solo uno por flujo)'
    )
  
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('nombre_interno') == 'solicitar_phone':
                vals['es_paso_telefono'] = True
        return super().create(vals_list)

    def write(self, vals):
        if vals.get('nombre_interno') == 'solicitar_phone':
            vals['es_paso_telefono'] = True
        elif 'nombre_interno' in vals and vals['nombre_interno'] != 'solicitar_phone':
            vals['es_paso_telefono'] = False
        return super().write(vals)