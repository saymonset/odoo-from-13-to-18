from odoo import models, fields, api

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
        compute='_compute_bcv_rate',
        store=True,
    )

    # ⚠ REEMPLAZA attrs ❌ por un campo booleano que controla readonly ✔
    is_bcv_editable = fields.Boolean(
        compute="_compute_is_bcv_editable",
        store=False
    )

    @api.depends('currency_id')
    def _compute_is_bcv_editable(self):
        for rec in self:
            rec.is_bcv_editable = rec.currency_id.name == 'VES'

    @api.depends('rate', 'currency_id')
    def _compute_bcv_rate(self):
        for record in self:
            if record.currency_id.name == 'VES' and record.rate:
                company_currency = record.company_id.currency_id

                if company_currency.name == 'USD':
                    record.bcv_rate_value = 1.0 / record.rate
                else:
                    usd_currency = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)
                    usd_rate = self.search([
                        ('currency_id', '=', usd_currency.id),
                        ('name', '=', record.name),
                        ('company_id', '=', record.company_id.id)
                    ], limit=1)

                    if usd_rate and usd_rate.rate:
                        record.bcv_rate_value = usd_rate.rate / record.rate
                    else:
                        record.bcv_rate_value = 0
            else:
                record.bcv_rate_value = 0
