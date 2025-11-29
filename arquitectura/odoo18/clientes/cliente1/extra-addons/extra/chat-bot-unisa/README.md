## Arquitectura y Componentes
 
chat-bot-unisa (Módulo de IA): Interfaz web para visualizar y gestionar mensajes, incorpora IA para transcripción y análisis de textos.
 
 Se puede heredar como lo hace Explorer Backend Theme para colocar un chat box en la web principal del portal

 1-) Configuracion del chat bot principal de entrada
 ```
 static/src/components/ChatBotWrapper/ChatBotWrapper.js
 ```


 2-) Copiar modulo a test
```
cp -r /home/odoo/odoo-from-13-to-18/arquitectura/odoo18/clientes/cliente1/extra-addons/extra/chat-bot-unisa /home/odoo/odoo-skeleton/n8n-evolution-api-odoo-18/v18/addons/extra
```