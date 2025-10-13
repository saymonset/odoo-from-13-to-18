# -*- coding: utf-8 -*-

import logging
import json
from odoo import models, api
from odoo.exceptions import ValidationError
import os
from pathlib import Path
import time
from datetime import datetime
from odoo.http import request

_logger = logging.getLogger(__name__)

class DailySummaryUCase(models.TransientModel):
    _name = 'daily_summary_queries.use.case'
    _description = 'daily_summary_queries Use Case'

    @staticmethod
    def format_date(date_value):
        """Método estático para formatear fechas"""
        if isinstance(date_value, datetime):
            return date_value.strftime('%Y-%m-%d')
        elif isinstance(date_value, str):
            try:
                return datetime.strptime(date_value, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
            except:
                return date_value
        return ''
    
    @api.model
    def execute(self, options)->dict:
        try:
            filtro_order_number = options.get('order_number')
            filtro_fecha = options.get('fecha')  # Opcional: '2024-01-15'
            # Consulta más simple
            query = """
                     SELECT 
                        (SELECT COUNT(*) FROM sale_order WHERE DATE(date_order) = CURRENT_DATE AND state NOT IN ('cancel', 'draft')) as pedidos_hoy,
                        (SELECT SUM(amount_total) FROM sale_order WHERE DATE(date_order) = CURRENT_DATE AND state NOT IN ('cancel', 'draft')) as ventas_hoy,
                        (SELECT COUNT(*) FROM purchase_order WHERE DATE(date_order) = CURRENT_DATE AND state NOT IN ('cancel', 'draft')) as compras_hoy,
                        (SELECT COUNT(*) FROM stock_quant sq JOIN stock_location sl ON sq.location_id = sl.id WHERE sq.quantity <= 0 AND sl.usage = 'internal') as productos_agotados;
                                    """
        
            params = []
            
            
            self.env.cr.execute(query, params)
            result_sql = self.env.cr.dictfetchall()
            
            # Preparar los datos
            result_data = []
            for result in result_sql:
                result_data.append({
                    'pedidos_hoy': result['pedidos_hoy'],
                    'ventas_hoy': result['ventas_hoy'],
                    'compras_hoy': result['compras_hoy'],
                    'productos_agotados': result['productos_agotados'],
                })
  
            return result_data
            
        except Exception as e:
            _logger.error(f"Error al procesar la solicitud: {str(e)}")
            return {"error": f"Error en el procesamiento: {str(e)}"}