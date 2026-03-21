import re
import logging
import requests
from bs4 import BeautifulSoup
import urllib3
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from psycopg2 import IntegrityError

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
_logger = logging.getLogger(__name__)


class BCVRateProvider(models.AbstractModel):
    _name = 'bcv.rate.provider'
    _description = 'Proveedor de tasas BCV'
    
    def get_bcv_rate(self):
        try:
            url = 'https://www.bcv.org.ve'
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

            response = requests.get(url, headers=headers, verify=False, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Buscar específicamente la línea o bloque del USD
            # Opción 1: buscar texto que contenga "USD" y extraer el número cercano
            text_blocks = soup.find_all(string=re.compile(r'(?i)USD', re.DOTALL))
            
            for block in text_blocks:
                # Buscar patrones como 123456,78901 o 123.456,78 cerca de USD
                match = re.search(r'(\d{1,3}(?:\.\d{3})*,\d{2,8})', block)
                if match:
                    tasa_str = match.group(1)
                    # Limpiar y convertir
                    cleaned = tasa_str.replace('.', '').replace(',', '.')
                    try:
                        tasa = float(cleaned)
                        if 100 < tasa < 1000000:  # Rango razonable para 2025-2026
                            _logger.info(f"Tasa BCV encontrada: {tasa} (de '{tasa_str}')")
                            return tasa
                    except ValueError:
                        pass

            # Opción 2: fallback - buscar en toda la página pero con más precisión
            full_text = soup.get_text(separator=' ', strip=True)
            match = re.search(r'(?i)USD\s*[\D]*?(\d{1,3}(?:\.\d{3})*,\d{2,8})', full_text)
            if match:
                tasa_str = match.group(1)
                cleaned = tasa_str.replace('.', '').replace(',', '.')
                tasa = float(cleaned)
                if 100 < tasa < 1000000:
                    return tasa

            _logger.warning("No se encontró tasa USD en la página BCV")
            return None

        except Exception as e:
            _logger.error(f"Error obteniendo tasa BCV: {e}", exc_info=True)
            return None


class BCVRateUpdate(models.Model):
    _name = 'bcv.rate.update'
    _description = 'Actualizador de tasa BCV'
    _inherit = ['bcv.rate.provider']
    
    name = fields.Char(default='Actualización BCV')
    update_date = fields.Datetime()
    last_rate = fields.Float(digits=(12, 4))
    status = fields.Selection([
        ('success', 'Éxito'),
        ('failed', 'Fallido'),
        ('pending', 'Pendiente')
    ], default='pending')

    def _get_or_create_currency(self, name, code, symbol):
        """Obtiene o crea una moneda usando sudo() para evitar restricciones de acceso.
        Busca incluso monedas inactivas y las activa si es necesario."""
        # Buscar con sudo() para evitar reglas de registro, y con active_test=False para incluir inactivas
        currency = self.env['res.currency'].sudo().with_context(active_test=False).search([
        ('name', '=', name),
    ], limit=1)
        
        if currency:
            # Si existe pero está inactiva, la activamos
            if not currency.active:
                currency.sudo().write({'active': True})
                _logger.info(f"Moneda {name} reactivada.")
            return currency

        # No existe, intentar crear
        try:
            currency = self.env['res.currency'].sudo().create({
                'name': name,
                'symbol': symbol,
                'active': True,
            })
            _logger.info(f"Moneda {name} creada automáticamente.")
            return currency
        except IntegrityError:
            # Ocurrió un conflicto de duplicado (otro proceso creó la moneda mientras tanto)
            self.env.cr.rollback()
            currency = self.env['res.currency'].sudo().with_context(active_test=False).search([
                ('name', '=', name),
            ], limit=1)
            if currency:
                if not currency.active:
                    currency.sudo().write({'active': True})
                _logger.info(f"Moneda {name} recuperada tras conflicto.")
                return currency
            else:
                raise UserError(f"No se pudo crear la moneda {name} tras reintentar. Por favor, créela manualmente.")

    def update_ves_rate_now(self):
        self.ensure_one()
        try:
            tasa = self.get_bcv_rate()
            if not tasa:
                raise UserError("No se pudo obtener la tasa BCV")

            # Obtener o crear las monedas VES y USD
            ves = self._get_or_create_currency('VES', 'VES', 'Bs.')
            usd = self._get_or_create_currency('USD', 'USD', '$')

            company = self.env.company
            base = company.currency_id

            if base == usd:
                rate = 1 / tasa
            else:
                usd_rate = self.env['res.currency.rate'].search([
                    ('currency_id', '=', usd.id)
                ], order='name desc', limit=1)

                if not usd_rate:
                    # Si no hay tasa USD, creamos una por defecto (1 USD = 1 USD)
                    _logger.warning("No existe tasa USD para convertir. Creando una por defecto.")
                    self.env['res.currency.rate'].create({
                        'currency_id': usd.id,
                        'name': fields.Date.today(),
                        'rate': 1.0,
                        'company_id': company.id,
                    })
                    usd_rate = self.env['res.currency.rate'].search([
                        ('currency_id', '=', usd.id)
                    ], order='name desc', limit=1)

                rate = (1 / tasa) * usd_rate.rate

            existing = self.env['res.currency.rate'].search([
                ('currency_id', '=', ves.id),
                ('name', '=', fields.Date.today()),
                ('company_id', '=', company.id)
            ], limit=1)

            if existing:
                existing.rate = rate
            else:
                self.env['res.currency.rate'].create({
                    'currency_id': ves.id,
                    'name': fields.Date.today(),
                    'rate': rate,
                    'company_id': company.id,
                })

            self.write({
                'status': 'success',
                'last_rate': tasa,
                'update_date': fields.Datetime.now()
            })

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Tasa BCV actualizada',
                    'message': f"1 USD = {tasa} VES",
                    'type': 'success'
                }
            }

        except Exception as e:
            # No escribimos 'failed' porque la transacción puede estar rota.
            # Simplemente relanzamos el error con un mensaje claro.
            raise UserError(f"ERROR: {e}")

    def update_ves_rate_cron(self):
        record = self.search([], limit=1)
        if not record:
            record = self.create({'name': 'Cron BCV'})
        record.update_ves_rate_now()