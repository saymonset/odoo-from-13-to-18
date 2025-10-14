# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from odoo import models, api

_logger = logging.getLogger(__name__)

class SaleOrderLineDetailsUseCase(models.TransientModel):
    _name = 'sale_order_line_details.use.case'
    _description = 'Detalle de líneas de pedido de venta (Use Case)'

    @staticmethod
    def format_date(date_value):
        """Formatea fechas en formato legible (YYYY-MM-DD)."""
        if not date_value:
            return ''
        try:
            if isinstance(date_value, datetime):
                return date_value.strftime('%Y-%m-%d')
            return datetime.strptime(str(date_value), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
        except Exception:
            return str(date_value)

    @api.model
    def execute(self, options) -> dict:
        """
        Consulta los detalles de líneas de venta según número de pedido (order_number).
        """
        try:
            filtro_order_number = options.get('order_number')
            if not filtro_order_number:
                return {"error": "Debe proporcionar un número de pedido (order_number)."}

            query = """
                SELECT 
                    so.name AS order_number,
                    so.date_order AS order_date,
                    so.effective_date AS effective_date,
                    partner.name AS customer_name,
                    shipping_address.street AS shipping_street,
                    shipping_address.city AS shipping_city,
                    st.name AS shipping_state,
                    c.name AS shipping_country,
                    pt.name AS product_name,
                    sol.product_uom_qty AS quantity,
                    sol.price_unit AS unit_price,
                    sol.price_subtotal AS subtotal
                FROM sale_order so
                JOIN res_partner partner ON so.partner_id = partner.id
                LEFT JOIN res_partner shipping_address ON so.partner_shipping_id = shipping_address.id
                LEFT JOIN res_country_state st ON shipping_address.state_id = st.id
                LEFT JOIN res_country c ON shipping_address.country_id = c.id
                JOIN sale_order_line sol ON so.id = sol.order_id
                JOIN product_product product ON sol.product_id = product.id
                JOIN product_template pt ON product.product_tmpl_id = pt.id
                WHERE so.name ILIKE %s
                ORDER BY so.id, sol.id;
            """

            params = [f"%{filtro_order_number}%"]
            self.env.cr.execute(query, params)
            results = self.env.cr.dictfetchall()

            if not results:
                return {"message": f"No se encontraron resultados para el pedido '{filtro_order_number}'."}

            formatted = []
            for row in results:
                formatted.append({
                    "order_number": row["order_number"],
                    "order_date": self.format_date(row["order_date"]),
                    "effective_date": self.format_date(row["effective_date"]),
                    "customer_name": row["customer_name"],
                    "shipping_address": f"{row['shipping_street'] or ''}, {row['shipping_city'] or ''}, {row['shipping_state'] or ''}, {row['shipping_country'] or ''}".strip(', '),
                    "product_name": row["product_name"],
                    "quantity": float(row["quantity"] or 0),
                    "unit_price": float(row["unit_price"] or 0),
                    "subtotal": float(row["subtotal"] or 0),
                })

            return {
                "pedido": filtro_order_number,
                "total_productos": len(formatted),
                "detalles": formatted
            }

        except Exception as e:
            _logger.error(f"Error al procesar la solicitud: {str(e)}")
            return {"error": f"Error en el procesamiento: {str(e)}"}
