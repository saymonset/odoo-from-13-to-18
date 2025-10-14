# -*- coding: utf-8 -*-
import logging
import json
from odoo import models, api
from datetime import datetime

_logger = logging.getLogger(__name__)

class DailySummaryUseCase(models.TransientModel):
    _name = 'daily_summary_queries.use.case'
    _description = 'Consulta resumida de ventas, compras, stock y moneda (por día, fecha o rango)'

    # ----------------------------------------------------------
    # MÉTODOS AUXILIARES
    # ----------------------------------------------------------

    @staticmethod
    def _normalize_date(date_value):
        """
        Normaliza la fecha al formato YYYY-MM-DD.
        Acepta formatos:
        - YYYY-MM-DD
        - DD/MM/YYYY
        - YYYY-MM-DD HH:MM:SS
        """
        if not date_value:
            return None

        if isinstance(date_value, datetime):
            return date_value.strftime('%Y-%m-%d')

        if isinstance(date_value, str):
            for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S'):
                try:
                    return datetime.strptime(date_value, fmt).strftime('%Y-%m-%d')
                except ValueError:
                    continue

        return None  # si no pudo parsearse, devuelve None

    def _build_date_conditions(self, options):
        """
        Construye la condición SQL y los parámetros de fecha según la solicitud del usuario.
        """
        date_from = self._normalize_date(options.get('date_from'))
        date_to = self._normalize_date(options.get('date_to'))
        specific_date = self._normalize_date(options.get('specific_date'))

        conditions = []
        params = []
        summary_type = ""

        if specific_date:
            conditions.append("DATE(date_order) = %s")
            params.append(specific_date)
            summary_type = "resumen_fecha_especifica"

        elif date_from and date_to:
            # Validación: si date_from > date_to, se intercambian
            if date_from > date_to:
                date_from, date_to = date_to, date_from
            conditions.append("DATE(date_order) BETWEEN %s AND %s")
            params.extend([date_from, date_to])
            summary_type = "resumen_rango_fechas"

        else:
            conditions.append("DATE(date_order) = CURRENT_DATE")
            summary_type = "resumen_dia_actual"

        return " AND ".join(conditions), params, summary_type

    def _get_company_currency(self):
        """Obtiene la información de la moneda base de la compañía actual."""
        company = self.env.company
        currency = company.currency_id
        return {
            "nombre_moneda": currency.name,
            "codigo_moneda": currency.currency_unit_label or currency.name,
            "simbolo_moneda": currency.symbol,
            "posicion_simbolo": currency.position,
            "id_moneda": currency.id,
        }

    def _get_period_description(self, options, summary_type):
        """Genera una descripción legible del periodo consultado."""
        if summary_type == "resumen_dia_actual":
            return "Resumen del día actual"
        elif summary_type == "resumen_fecha_especifica":
            return f"Resumen del día {options.get('specific_date')}"
        elif summary_type == "resumen_rango_fechas":
            return f"Resumen del periodo desde {options.get('date_from')} hasta {options.get('date_to')}"
        return "Resumen sin periodo definido"

    # ----------------------------------------------------------
    # MÉTODO PRINCIPAL
    # ----------------------------------------------------------
    @api.model
    def execute(self, options) -> dict:
        """Ejecuta la consulta SQL y devuelve un resumen seguro."""
        try:
            date_condition, date_params, summary_type = self._build_date_conditions(options)

            # Por esto:
            if not date_condition:
                return {"error": "No se pudo construir una condición de fecha válida."}

            # Si no hay parámetros pero el resumen es 'resumen_dia_actual', no pasa nada.
            if not date_params and summary_type != "resumen_dia_actual":
                return {"error": "Las fechas proporcionadas no son válidas."}

            # --- 🔧 Query optimizado con CTEs ---
            query = f"""
                WITH ventas AS (
                    SELECT * FROM sale_order
                    WHERE {date_condition}
                    AND state NOT IN ('cancel', 'draft')
                ),
                compras AS (
                    SELECT * FROM purchase_order
                    WHERE {date_condition}
                    AND state NOT IN ('cancel', 'draft')
                )
                SELECT
                    (SELECT COUNT(*) FROM ventas) AS total_pedidos,
                    (SELECT COALESCE(SUM(amount_total), 0) FROM ventas) AS total_ventas,
                    (SELECT COUNT(*) FROM compras) AS total_compras,
                    (SELECT COUNT(*) 
                    FROM stock_quant sq
                    JOIN stock_location sl ON sq.location_id = sl.id
                    WHERE sq.quantity <= 0 
                    AND sl.usage = 'internal') AS productos_sin_stock;
            """

            # Duplicamos los parámetros para ventas y compras
            final_params = date_params * 2

            try:
                self.env.cr.execute(query, final_params)
                result_sql = self.env.cr.dictfetchall()
            except Exception as sql_error:
                _logger.error(f"Error SQL: {str(sql_error)}")
                return {"error": f"Error al ejecutar la consulta SQL: {str(sql_error)}"}

            if not result_sql or len(result_sql) == 0:
                return {
                    "tipo_resumen": summary_type,
                    "descripcion_periodo": self._get_period_description(options, summary_type),
                    "datos": {
                        "total_pedidos": 0,
                        "total_ventas": 0.0,
                        "total_compras": 0,
                        "productos_sin_stock": 0,
                    },
                    "parametros": options,
                    "moneda": self._get_company_currency(),
                    "message": "No se encontraron datos para el periodo solicitado."
                }

            result = result_sql[0]

            response = {
                "tipo_resumen": summary_type,
                "descripcion_periodo": self._get_period_description(options, summary_type),
                "datos": {
                    "total_pedidos": result.get('total_pedidos', 0),
                    "total_ventas": float(result.get('total_ventas', 0) or 0.0),
                    "total_compras": result.get('total_compras', 0),
                    "productos_sin_stock": result.get('productos_sin_stock', 0),
                },
                "parametros": options,
                "moneda": self._get_company_currency()
            }

            return response

        except Exception as e:
            _logger.error(f"Error general en execute(): {str(e)}")
            return {"error": f"Error inesperado: {str(e)}"}
