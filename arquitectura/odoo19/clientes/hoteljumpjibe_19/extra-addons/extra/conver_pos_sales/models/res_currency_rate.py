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
        """Extrae la tasa oficial del USD del sitio del BCV de forma más confiable."""
        try:
            url = 'https://www.bcv.org.ve'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                              '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }

            response = requests.get(url, headers=headers, verify=False, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Buscar bloques que contengan "USD" (case insensitive)
            text_blocks = soup.find_all(string=re.compile(r'(?i)USD', re.DOTALL | re.IGNORECASE))

            for block in text_blocks:
                # Buscar número con formato BCV: miles con punto, decimal con coma, hasta 8 decimales
                match = re.search(r'(\d{1,3}(?:\.\d{3})*,\d{2,8})', block)
                if match:
                    tasa_str = match.group(1)
                    # Limpiar: quitar puntos de miles, cambiar coma por punto decimal
                    cleaned = tasa_str.replace('.', '').replace(',', '.')
                    try:
                        tasa = float(cleaned)
                        # Rango realista para tasa BCV actual (2025-2026)
                        if 100 < tasa < 2000000:
                            _logger.info(f"Tasa BCV detectada: {tasa} (texto: '{tasa_str}')")
                            return tasa
                    except ValueError:
                        continue

            # Fallback: buscar en todo el texto plano
            full_text = soup.get_text(separator=' ', strip=True)
            match = re.search(r'(?i)USD\s*[^0-9]*?(\d{1,3}(?:\.\d{3})*,\d{2,8})', full_text)
            if match:
                tasa_str = match.group(1)
                cleaned = tasa_str.replace('.', '').replace(',', '.')
                tasa = float(cleaned)
                if 100 < tasa < 2000000:
                    _logger.info(f"Tasa BCV fallback: {tasa}")
                    return tasa

            _logger.warning("No se pudo extraer la tasa USD del BCV")
            return None

        except Exception as e:
            _logger.error(f"Error al obtener tasa BCV: {e}", exc_info=True)
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
        currency = self.env['res.currency'].sudo().with_context(active_test=False).search([
            ('name', '=', name),
        ], limit=1)

        if currency:
            if not currency.active:
                currency.sudo().write({'active': True})
                _logger.info(f"Moneda {name} reactivada.")
            return currency

        try:
            currency = self.env['res.currency'].sudo().create({
                'name': name,
                'symbol': symbol,
                'active': True,
            })
            _logger.info(f"Moneda {name} creada automáticamente.")
            return currency
        except IntegrityError:
            self.env.cr.rollback()
            currency = self.env['res.currency'].sudo().with_context(active_test=False).search([
                ('name', '=', name),
            ], limit=1)
            if currency:
                if not currency.active:
                    currency.sudo().write({'active': True})
                _logger.info(f"Moneda {name} recuperada tras conflicto.")
                return currency
            raise UserError(f"No se pudo crear la moneda {name}. Créela manualmente.")

    def update_ves_rate_now(self):
        self.ensure_one()
        try:
            tasa = self.get_bcv_rate()
            if not tasa:
                raise UserError("No se pudo obtener la tasa del BCV. Verifique el sitio o los logs.")

            ves = self._get_or_create_currency('VES', 'VES', 'Bs.')
            usd = self._get_or_create_currency('USD', 'USD', '$')

            company = self.env.company
            base = company.currency_id

            if base == usd:
                rate = 1 / tasa  # 1 VES = rate USD
            else:
                usd_rate = self.env['res.currency.rate'].search([
                    ('currency_id', '=', usd.id),
                    ('name', '=', fields.Date.today()),
                    ('company_id', '=', company.id),
                ], order='name desc', limit=1)

                if not usd_rate:
                    _logger.warning("Creando tasa USD por defecto (1.0)")
                    self.env['res.currency.rate'].create({
                        'currency_id': usd.id,
                        'name': fields.Date.today(),
                        'rate': 1.0,
                        'company_id': company.id,
                    })
                    usd_rate = self.env['res.currency.rate'].search([
                        ('currency_id', '=', usd.id),
                    ], order='name desc', limit=1)

                rate = (1 / tasa) * usd_rate.rate

            existing = self.env['res.currency.rate'].search([
                ('currency_id', '=', ves.id),
                ('name', '=', fields.Date.today()),
                ('company_id', '=', company.id)
            ], limit=1)

            if existing:
                existing.write({
                    'rate': rate,
                    'is_bcv_rate': True,
                    'source': 'bcv',
                    'bcv_rate_value': tasa,  # Guardamos el valor original BCV
                })
            else:
                self.env['res.currency.rate'].create({
                    'currency_id': ves.id,
                    'name': fields.Date.today(),
                    'rate': rate,
                    'company_id': company.id,
                    'is_bcv_rate': True,
                    'source': 'bcv',
                    'bcv_rate_value': tasa,
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
                    'message': f"1 USD = {tasa:.8f} VES",
                    'type': 'success',
                    'sticky': False,
                }
            }

        except Exception as e:
            raise UserError(f"Error al actualizar tasa BCV: {str(e)}")

    def update_ves_rate_cron(self):
        # Crea un nuevo registro para esta ejecución del cron
        new_record = self.sudo().create({
            'name': 'Cron BCV - ' + str(fields.Datetime.now()),      # Puedes cambiar el nombre si quieres diferenciarlo
            'status': 'pending',
        })
        new_record.update_ves_rate_now()


class ResCurrencyRate(models.Model):
    _inherit = 'res.currency.rate'

    is_bcv_rate = fields.Boolean('Tasa BCV', default=False)
    source = fields.Selection([
        ('bcv', 'BCV Oficial'),
        ('parallel', 'Paralelo'),
        ('other', 'Otra Fuente'),
    ], string='Fuente', default='other')

    bcv_rate_value = fields.Float(
        'Tasa BCV (1 USD = X VES)',
        digits=(12, 4),
        help="Valor original publicado por BCV (1 USD = este valor en VES)"
    )

    is_bcv_editable = fields.Boolean(
        compute='_compute_is_bcv_editable',
        store=False,
    )

    @api.depends('currency_id')
    def _compute_is_bcv_editable(self):
        for rec in self:
            rec.is_bcv_editable = (rec.currency_id.name == 'VES')

   