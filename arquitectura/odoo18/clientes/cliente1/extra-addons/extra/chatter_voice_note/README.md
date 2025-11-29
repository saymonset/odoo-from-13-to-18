Un modulo que desde un audio que se agarra, lo traduce en un texto y tambien viene e;l texto aparte analizado con la ia
Hace con ese texto un reporte pdf

Recibe parametros del backend, fue rudo la solucion. en a_hospital

# copiar a test
# Pasar tu modulo a test
```bash
0-) Instalar el modulo pdfmake o debe estar en dependence
```
cp -r /home/odoo/odoo-from-13-to-18/arquitectura/odoo18/clientes/cliente1/extra-addons/extra/pdfmake /home/odoo/odoo-skeleton/n8n-evolution-api-odoo-18/v18/addons/extra
```
1-) En Constantes debes cambiar a test la url. La ruta de la constante.js es
/home/odoo/odoo-from-13-to-18/arquitectura/odoo18/clientes/cliente1/extra-addons/extra/chatter_voice_note/static/src/components/audio_to_text/constants.js
2-) en  medical_report_controller debes # URL del webhook de n8n, test: test-medical-report
3-) En Ajustes/tecnico/Parámetros del sistema configurar clave/valor
clave: medical_report.n8n_webhook_url
valor: https://n8n.jumpjibe.com/webhook/test-medical-report

cp -r /home/odoo/odoo-from-13-to-18/arquitectura/odoo18/clientes/cliente1/extra-addons/extra/chatter_voice_note /home/odoo/odoo-skeleton/n8n-evolution-api-odoo-18/v18/addons/extra
```
# Copiar a produccion
```bash
0-) Instalar el modulo pdfmake o debe estar en dependence
cp -r /home/odoo/odoo-from-13-to-18/arquitectura/odoo18/clientes/cliente1/extra-addons/extra/pdfmake /home/odoo/odoo-skeleton/leads/odoo_instancia_2/v18_2/addons/extra
```
```bash

1-) En Constantes debes cambiar a produccion la url. La ruta de la constante.js es
/home/odoo/odoo-from-13-to-18/arquitectura/odoo18/clientes/cliente1/extra-addons/extra/chatter_voice_note/static/src/components/audio_to_text/constants.js

2-) En Ajustes/Tecnico/Parametros -> Parámetros del sistema,  configurar clave/valor
clave: medical_report.n8n_webhook_url
valor: https://n8n.jumpjibe.com/webhook/medical-report
```
# Pasar tu modulo a produccion
```bash

3-) cp -r /home/odoo/odoo-from-13-to-18/arquitectura/odoo18/clientes/cliente1/extra-addons/extra/chatter_voice_note /home/odoo/odoo-skeleton/leads/odoo_instancia_2/v18_2/addons/extra


```


cp -r /home/odoo/odoo-from-13-to-18/arquitectura/odoo18/clientes/cliente1/extra-addons/extra/chat-bot-n8n-ia /home/odoo/odoo-skeleton/leads/odoo_instancia_2/v18_2/addons/extra