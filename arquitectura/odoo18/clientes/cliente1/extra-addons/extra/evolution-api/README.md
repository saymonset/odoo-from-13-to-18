## Arquitectura y Componentes
WhatsApp Gateway: Recibe y envía mensajes entre WhatsApp y Evolution API.

n8n: Orquesta los flujos automáticos (por ejemplo: crear clientes, registrar reservas, enviar respuestas automáticas).

chat-bot-n8n-ia (Módulo de IA): Interfaz web para visualizar y gestionar mensajes, incorpora IA para transcripción y análisis de textos.

Base de Datos Odoo: Almacena los datos de clientes, mensajes y transcripciones para uso histórico y operativo.
## Proceso 
   0-) Inyectamos IA en 'depends': ['chat-bot-n8n-ia']
   1-) Controler
   2-) service
   3-)use case
## Flujo de Trabajo
1. Un huésped envía un audio por WhatsApp solicitando una reserva.
2. Evolution API recibe el audio, identifica el número de teléfono y lo clasifica.
3. La IA transcribe el audio a texto automáticamente.
4. El mensaje y la transcripción se guardan en Odoo.
5. n8n detecta la solicitud y puede:
    - Crear un registro de lead/reserva en Odoo
    - Enviar una respuesta automática al huésped
    - Notificar al equipo de reservas del hotel
