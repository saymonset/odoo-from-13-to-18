Un modulo que desde un audio que se graba, lo traduce en un texto y tambien viene el texto aparte analizado con la ia
Hace con ese texto un reporte pdf

######## N8N. JSON ###########
//TEST
// el n8n es /personal/lead/unisa/voz-to-text/tests-voz-to-text
// En path del webhook, se coloca test-audios para entorno de pruebas
  
// En path del webhook, se coloca audios para entorno de produccion
  //#  PRODUCCION
  //el n8n es personal/lead/unisa/voz-to-text/prod-voz-to-text
######## END N8N ###########

# copiar a test
# Pasar tu modulo a test
```bash
0-) Instalar el modulo pdfmake o debe estar en dependence
```
cp -r /home/odoo/odoo-from-13-to-18/arquitectura/odoo18/clientes/cliente1/extra-addons/extra/pdfmake /home/odoo/odoo-skeleton/n8n-evolution-api-odoo-18/v18/addons/extra
```
1-) En Constantes debes cambiar a test la url. La ruta de la constante.js es
/home/odoo/odoo-from-13-to-18/arquitectura/odoo18/clientes/cliente1/extra-addons/extra/chatter_voice_note/static/src/components/audio_to_text/constants.js

2-) En Ajustes/tecnico/Parámetros del sistema configurar clave/valor
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