# copiar a test
# Pasar tu modulo a test
```bash
1-) En Constantes debes cambiar a test la url. La ruta de la constante.js es
/home/odoo/odoo-from-13-to-18/arquitectura/odoo18/clientes/cliente1/extra-addons/extra/chatter_voice_note/static/src/components/audio_to_text/constants.js
2-) en  medical_report_controller debes # URL del webhook de n8n, test: test-medical-report
3-) En Parámetros del sistema configurar clave/valor
clave: medical_report.n8n_webhook_url
valor: https://n8n.jumpjibe.com/webhook/test-medical-report

cp -r /home/odoo/odoo-from-13-to-18/arquitectura/odoo18/clientes/cliente1/extra-addons/extra/chatter_voice_note /home/odoo/odoo-skeleton/n8n-evolution-api-odoo-18/v18/addons/extra
```
# Copiar a produccion
```bash
1-) En Constantes debes cambiar a produccion la url. La ruta de la constante.js es
/home/odoo/odoo-from-13-to-18/arquitectura/odoo18/clientes/cliente1/extra-addons/extra/chatter_voice_note/static/src/components/audio_to_text/constants.js
2-) en  medical_report_controller debes # URL del webhook de n8n, produccion: medical-report
3-) En Parámetros del sistema configurar clave/valor
clave: medical_report.n8n_webhook_url
valor: https://n8n.jumpjibe.com/webhook/medical-report
```
# Pasar tu modulo a produccion
```bash
2-) cp -r /home/odoo/odoo-from-13-to-18/arquitectura/odoo18/clientes/cliente1/extra-addons/extra/chatter_voice_note /home/odoo/odoo-skeleton/leads/odoo_instancia_2/v18_2/addons/extra


```


cp -r /home/odoo/odoo-from-13-to-18/arquitectura/odoo18/clientes/cliente1/extra-addons/extra/chat-bot-n8n-ia /home/odoo/odoo-skeleton/leads/odoo_instancia_2/v18_2/addons/extra