import re
import logging
import requests
from bs4 import BeautifulSoup
import urllib3
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
_logger = logging.getLogger(__name__)


class BCVRateProvider(models.AbstractModel):
    _name = 'bcv.rate.provider'
    _description = 'Proveedor de tasas BCV'
    
    def get_bcv_rate(self):
        try:
            url = 'https://www.bcv.org.ve'
            headers = {'User-Agent': 'Mozilla/5.0'}

            response = requests.get(url, headers=headers, verify=False, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text()

            tasas = re.findall(r'\b\d{1,3}(?:\.\d{3})*,\d{2,4}\b', text)
            valores = []

            for t in tasas:
                try:
                    num = float(t.replace('.', '').replace(',', '.'))
                    if 30 <= num <= 200000:
                        valores.append(num)
                except:
                    pass

            if valores:
                return valores[0]

            return None

        except Exception as e:
            _logger.error(f"Error BCV: {e}")
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

    def update_ves_rate_now(self):
        self.ensure_one()
        try:
            tasa = self.get_bcv_rate()
            if not tasa:
                raise UserError("No se pudo obtener la tasa BCV")

            ves = self.env['res.currency'].search([('name', '=', 'VES')], limit=1)
            usd = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)

            if not ves or not usd:
                raise UserError("Faltan monedas VES o USD")

            company = self.env.company
            base = company.currency_id

            if base == usd:
                rate = 1 / tasa
            else:
                usd_rate = self.env['res.currency.rate'].search([
                    ('currency_id', '=', usd.id)
                ], order='name desc', limit=1)

                if not usd_rate:
                    raise UserError("No existe tasa USD para convertir")

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
            self.write({'status': 'failed'})
            raise UserError(f"ERROR: {e}")

    def update_ves_rate_cron(self):
        record = self.search([], limit=1)
        if not record:
            record = self.create({'name': 'Cron BCV'})
        record.update_ves_rate_now()