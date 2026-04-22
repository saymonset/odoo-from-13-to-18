from odoo import models, fields, api
from datetime import datetime
class Website(models.Model):
    _inherit = 'website'

    def get_bcv_rate(self):
        """Retorna la tasa USD/VES actual (cuántos bolívares por 1 USD)"""
        # Buscar la tasa más reciente para VES
        rate = self.env['res.currency.rate'].search([
            ('currency_id.name', '=', 'VES'),
            ('company_id', '=', self.env.company.id),
        ], order='name desc', limit=1)

        if rate and rate.rate:
            # La tasa almacenada es VES por 1 USD? Depende de la moneda base.
            # En Odoo, la tasa se guarda como la relación entre la moneda y la moneda base.
            # Si la moneda base es USD, entonces la tasa para VES es VES por 1 USD.
            # Si la moneda base es VES, entonces la tasa para USD es USD por 1 VES.
            # Para obtener el valor en USD a partir de VES, necesitamos invertir si es necesario.
            # Vamos a suponer que la moneda de la compañía es VES (como en tu caso) y que la tasa
            # almacenada es la cantidad de USD por 1 VES? No, porque tu código en `update_ves_rate_now`
            # almacena la tasa de VES hacia la moneda base. Si la moneda base es VES, la tasa
            # para la moneda VES sería 1 (porque es la base), pero tú creas la tasa para VES
            # con `rate = (1 / tasa) * usd_rate.rate`. Vamos a analizar tu código:
            #
            #   if base == usd:
            #       rate = 1 / tasa
            #   else:
            #       usd_rate = ...  (tasa de USD con fecha actual)
            #       rate = (1 / tasa) * usd_rate.rate
            #
            # Luego guardas esa `rate` como la tasa de la moneda VES. Entonces esa tasa es la
            # cantidad de la moneda base por 1 VES. Si la moneda base es VES, entonces la tasa es 1.
            # Si la moneda base es USD, entonces la tasa es el valor en USD de 1 VES.
            # Para convertir VES a USD, multiplicamos por esa tasa.
            #
            # Pero lo más simple es que crees un campo `bcv_rate_value` en `res.currency.rate`
            # que guarde el valor original de BCV (1 USD = X VES). Luego lo usas directamente.
            # Tu código ya guarda `bcv_rate_value` en `res.currency.rate` (porque en
            # `update_ves_rate_now` escribes `'bcv_rate_value': tasa`). Así que podemos usar eso.
            if rate.bcv_rate_value:
                return rate.bcv_rate_value  # 1 USD = X VES
        return 1.0  # fallback

    def get_conversion_factor_ves_to_usd(self):
        """Retorna el factor para convertir VES a USD (precio_VES / factor = precio_USD)"""
        # Si la tasa BCV es 1 USD = X VES, entonces precio_USD = precio_VES / X


        rate = self.get_bcv_rate()
        if rate:
            return 1.0 / rate
        return 1.0
    
    def get_bcv_rate_info(self):
        """Retorna un dict con la tasa BCV (1 USD = X VES) y su fecha formateada"""
        rate_record = self.env['res.currency.rate'].search([
            ('currency_id.name', '=', 'VES'),
            ('is_bcv_rate', '=', True),
            ('company_id', '=', self.env.company.id),
        ], order='name desc', limit=1)

        if rate_record and rate_record.bcv_rate_value:
            # rate_record.name es un objeto date (ej: datetime.date(2026, 3, 30))
            fecha = rate_record.name
            # Formatear a dd/MM/yyyy
            fecha_formateada = fecha.strftime('%d/%m/%Y') if fecha else ''
            return {
                'rate': rate_record.bcv_rate_value,
                'date': rate_record.name,
                'date_formatted': fecha_formateada,
                'rate_display': f"1 USD = {rate_record.bcv_rate_value:,.4f} VES",
            }
        return {
            'rate': 1.0,
            'date': None,
            'date_formatted': '',
            'rate_display': 'Tasa no disponible',
        }