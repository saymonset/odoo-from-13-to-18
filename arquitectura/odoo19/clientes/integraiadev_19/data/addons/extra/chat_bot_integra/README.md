## Debes actualizar la bd
```bash
          # 1. Conéctate a PostgreSQL
          docker exec -it odoo-db18-n8n bash
          psql -U integraiadev -d dbintegraiadev
          # deprecated , solo para local : sudo -u postgres psql


          # 3. Agrega la columna birthdate (ESTO ES CRÍTICO)
          ALTER TABLE res_partner ADD COLUMN birthdate DATE;

          # 4. Verifica que se creó
          \d res_partner | grep birthdate

          # 5. Salir
          \q
```
## Arquitectura y Componentes
 
chat_bot_integra (Módulo de IA): Interfaz web para visualizar y gestionar mensajes, incorpora IA para transcripción y análisis de textos.
 
 # Primero debex instalar 
```bash
     Intalar el modulo  chat_bot_integra en odoo 
```

 0-) Copiar modulo a test
```
1-)



# En el webhook de n8n en la herramienta httprequest:  capturar_lead_odoo1
# Cambiar a https://integraia.lat/chat_bot_integra/capturar_lead

2-)
cp -r /home/odoo/odoo-from-13-to-18/arquitectura/odoo18/clientes/cliente1/extra-addons/extra/chat_bot_integra /home/odoo/odoo-skeleton/n8n-evolution-api-odoo-18/v18/addons/extra
```

###################   PRODUCCION      ##############
0-) Copiar modulo a prodccion

```
1-) 
# En el webhook de n8n en la herramienta httprequest:  capturar_lead_odoo1
# Cambiar a https://lead.integraia.lat/chat_bot_integra/capturar_lead

2-)
cp -r /home/odoo/odoo-from-13-to-18/arquitectura/odoo18/clientes/cliente1/extra-addons/extra/chat_bot_integra //home/odoo/odoo-skeleton/leads/odoo_instancia_2/v18_2/addons/extra
```

Opción 1: Regla por Etiqueta
yaml
Ir a: CRM → Configuración → Automatización → Reglas de Automatización
Nombre: "Procesar Leads WhatsApp Bot"
Condición: Etiquetas → contiene → WhatsApp Bot
Acciones: [Las que necesites]