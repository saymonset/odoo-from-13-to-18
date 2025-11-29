## Arquitectura y Componentes
 
chat-bot-unisa (Módulo de IA): Interfaz web para visualizar y gestionar mensajes, incorpora IA para transcripción y análisis de textos.
 
 0-) Copiar modulo a test
```
cp -r /home/odoo/odoo-from-13-to-18/arquitectura/odoo18/clientes/cliente1/extra-addons/extra/chat-bot-unisa /home/odoo/odoo-skeleton/n8n-evolution-api-odoo-18/v18/addons/extra
```

###################   PRODUCCION      ##############
0-) Copiar modulo a prodccion

```
cp -r /home/odoo/odoo-from-13-to-18/arquitectura/odoo18/clientes/cliente1/extra-addons/extra/chat-bot-unisa //home/odoo/odoo-skeleton/leads/odoo_instancia_2/v18_2/addons/extra
```

Opción 1: Regla por Etiqueta
yaml
Ir a: CRM → Configuración → Automatización → Reglas de Automatización
Nombre: "Procesar Leads WhatsApp Bot"
Condición: Etiquetas → contiene → WhatsApp Bot
Acciones: [Las que necesites]