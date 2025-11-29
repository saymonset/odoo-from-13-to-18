
1-) En /home/odoo/odoo-from-13-to-18/arquitectura/odoo18/clientes/cliente1/extra-addons/extra/rag_unisa/views/chat_bot_client_templates.xml , debes colocar el id del n8n chat bot
```
 props='{"webhookUrl": "https://n8n.jumpjibe.com/webhook/2b4e566c-dbd6-4deb-af84-8a8fddd16830/chat"}'/>
```

2-) Copiar modulo a test
```
cp -r /home/odoo/odoo-from-13-to-18/arquitectura/odoo18/clientes/cliente1/extra-addons/extra/rag_unisa /home/odoo/odoo-skeleton/n8n-evolution-api-odoo-18/v18/addons/extra
```