from odoo import http
from odoo.http import request
import json  # Importar el módulo json


class SaleOrderController(http.Controller):
    @http.route('/convert_price', type='json', auth='user')
    def convert_price(self):
        try:
            raw_data = request.httprequest.data
            params = json.loads(raw_data.decode('utf-8'))
            price_unit = params.get('price_unit')
            from_currency = params.get('from_currency')
            to_currency = params.get('to_currency')

            if not price_unit or not from_currency or not to_currency:
                return {"error": "Faltan parámetros: 'price_unit', 'from_currency' o 'to_currency'"}

            from_currency_obj = request.env['res.currency'].search([('name', '=', from_currency)], limit=1)
            to_currency_obj = request.env['res.currency'].search([('name', '=', to_currency)], limit=1)

            if not from_currency_obj or not to_currency_obj:
                return {"error": "Moneda no encontrada"}

            converted_price = request.env['sale.order'].convert_price_to_currency(
                price_unit, from_currency_obj, to_currency_obj
            )
            return {"converted_price": converted_price}
        except Exception as e:
            return {"error": str(e)}
        
    @http.route('/simple_test', type='json', auth='public')
    def simple_test(self):
         return {"message": "Hello, World!"}
    
    
    @http.route('/test', type='json', auth='public')
    def convert_price0(self):
        try:
            
            raw_data = request.httprequest.data
            params = json.loads(raw_data.decode('utf-8'))
            price_unit = params.get('price_unit')
            from_currency = params.get('from_currency')
            to_currency = params.get('to_currency')

            if not price_unit or not from_currency or not to_currency:
                return {"error": "Faltan parámetros: 'price_unit', 'from_currency' o 'to_currency'"}

            from_currency_obj = request.env['res.currency'].search([('name', '=', from_currency)], limit=1)
            to_currency_obj = request.env['res.currency'].search([('name', '=', to_currency)], limit=1)

            if not from_currency_obj or not to_currency_obj:
                return {"error": "Moneda no encontrada"}

            converted_price = request.env['sale.order'].convert_price_to_currency(
                price_unit, from_currency_obj, to_currency_obj
            )
            return {"converted_price": converted_price}
        except Exception as e:
            return {"error": str(e)}
