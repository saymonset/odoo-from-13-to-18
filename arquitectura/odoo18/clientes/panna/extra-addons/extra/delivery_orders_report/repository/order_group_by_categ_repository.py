from odoo import models
import json
# from .utils import obtener_titulo


class DeliveryCategoryGroup(models.TransientModel):
    _name = "delivery.category.group"

    @staticmethod
    def delivery_category_group(wizard):
        pickingTypeId = None
        pickingTypeName = ""
        placeOfDeliveryId = None
        almacenOriginId = None
        almacenOriginName = ""

        if wizard.place_of_delivery_ids:
            for place_of_delivery in wizard.place_of_delivery_ids:
                placeOfDeliveryId = place_of_delivery.id

        if wizard.stock_picking_type_ids:
            for picking_type in wizard.stock_picking_type_ids:
                pickingTypeId = picking_type.id
                pickingTypeName = picking_type.name

        if wizard.stock_locations_ids:
            for almacenOrigin in wizard.stock_locations_ids:
                almacenOriginId = almacenOrigin.id
                almacenOriginName = almacenOrigin.name

        # Inicializar la consulta SQL y los parámetros
        query = """
            SELECT
                TO_CHAR(picking.date, 'DD/MM/YYYY'),
                stock_picking_type.name AS tipo_transferencia,
                stock_location.name AS almacenOriginName,
                TO_CHAR(picking.scheduled_date, 'DD/MM/YYYY') AS scheduled_date,
                partner.name AS lugar_entrega,
                picking.origin AS folio,
                SUM(move.quantity) AS cantidad,
                productmpl.name AS nombre_producto,
                product_category.name AS categoria,
                productmpl.id as idProducto,
                productmpl.default_code as referencia
            FROM
                stock_picking AS picking
            JOIN
                stock_move AS move ON move.picking_id = picking.id
            JOIN
                product_product AS product ON product.id = move.product_id
            JOIN
                product_template AS productmpl ON productmpl.id = product.product_tmpl_id
            LEFT JOIN
                res_partner AS partner ON partner.id = picking.partner_id
            JOIN
                stock_picking_type AS stock_picking_type ON stock_picking_type.id = picking.picking_type_id
            JOIN
                stock_location ON stock_location.id = picking.location_id
            JOIN
                product_category  on product_category.id = productmpl.categ_id
            WHERE
                (stock_picking_type.id = %(type_id)s OR %(type_id)s IS NULL)
                AND (partner.id = %(place_id)s OR %(place_id)s IS NULL)
                AND (stock_location.id = %(almacen_origin)s OR %(almacen_origin)s IS NULL)
        """

        # Inicializar la lista de parámetros
        params = {
            "type_id": pickingTypeId,
            "place_id": placeOfDeliveryId,
            "almacen_origin": almacenOriginId,
        }

        # Agregar condiciones de fecha si están disponibles
        if wizard.scheduled_date:
            formatted_scheduled_date = wizard.scheduled_date.strftime("%d/%m/%Y")
            query += " AND TO_CHAR(picking.scheduled_date, 'DD/MM/YYYY') = %(scheduled_date)s"
            params["scheduled_date"] = formatted_scheduled_date

        query += """
            GROUP BY
                stock_picking_type.name,
                partner.name,
                picking.origin,
                picking.date,
                productmpl.name,
                stock_location.name,
                product_category.name,
                productmpl.id,
                TO_CHAR(picking.scheduled_date, 'DD/MM/YYYY')
            ORDER BY
                TO_CHAR(picking.scheduled_date, 'DD/MM/YYYY'),
                product_category.name;
        """

        # Ejecutar la consulta
        wizard.env.cr.execute(query, params)
        result = wizard.env.cr.fetchall()

        # Transformar el resultado SQL en un formato adecuado para el reporte
        docs_list = []
        agrupadoPorFirstTime = {}
        for row in result:
            categoria = row[8]
            # Si la categoría no está en agrupadoPorFirstTime, inicializa un arreglo vacío
            if categoria not in agrupadoPorFirstTime:
                agrupadoPorFirstTime[categoria] = []

            referencia = row[10] if row[10] else ""
            # Agrega el elemento actual al arreglo de la categoría
            agrupadoPorFirstTime[categoria].append(
                {
                    "group_key": row[8],
                    "lugar_entrega": row[4],
                    "folio": row[5],
                    "cantidad": row[6],
                    "nombre_producto": referencia + " " + row[7]["es_MX"]
                    if row[7]
                    else "",
                    "categoria": categoria,
                    "idProducto": row[9],
                }
            )

        # Ordenar cada lista de elementos por 'categoria' o cualquier otro campo que desees
        for categoria, items in agrupadoPorFirstTime.items():
            items.sort(
                key=lambda x: x["categoria"]
            )  # Cambia 'categoria' por el campo que desees usar para ordenar

        # Construir el objeto para bodyreport
        categorias_ordenadas = []
        for categoria, items in agrupadoPorFirstTime.items():
            categorias_ordenadas.append(
                {
                    "categoria": categoria,
                    "items": items,  # Aquí se agregan los elementos de cada categoría
                }
            )

        bodyreport = {
            "tipo_transferencia": pickingTypeName,
            "almacenOriginName": almacenOriginName,
            "scheduled_date": wizard.scheduled_date.strftime("%d/%m/%Y")
            if wizard.scheduled_date
            else None,
            "categorias": categorias_ordenadas,
        }

        return json.dumps(bodyreport)
