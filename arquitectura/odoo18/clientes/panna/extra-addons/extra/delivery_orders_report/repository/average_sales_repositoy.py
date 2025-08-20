from odoo import models
from datetime import datetime  # Importar el módulo datetime


class AverageSale(models.TransientModel):
    _name = "delivery.category.group"

    @staticmethod
    def average_sale(wizard):
        pricelist_ids = []
        expense_percentage = 0

        if wizard.pricelist_ids:
            for pricelist in wizard.pricelist_ids:
                pricelist_ids.append(pricelist.id)

        if wizard.expense_percentage:
            expense_percentage = wizard.expense_percentage

        # Inicializar la consulta SQL y los parámetros
        query = """
        SELECT
                product_template.default_code referencia ,
                product_template.id productId  ,
                product_template.name nombre,
                product_pricelist.id priceListId,
                product_pricelist.name,
                product_category.id categoryId,
                product_category.name

            FROM
                product_template
            JOIN
                product_category on product_category.id = product_template.categ_id
            JOIN  -- Cambiado a LEFT JOIN
                product_pricelist_item ON product_pricelist_item.categ_id = product_category.id
            JOIN  -- Cambiado a LEFT JOIN
                product_pricelist ON product_pricelist.id = product_pricelist_item.pricelist_id



            WHERE
                product_pricelist.id in ( %(priceList_id_1)s , %(priceList_id_2)s)
        """

        # Inicializar la lista de parámetros
        params = {
            "priceList_id_1": pricelist_ids[0] if len(pricelist_ids) > 0 else -1,
            "priceList_id_2": pricelist_ids[1] if len(pricelist_ids) > 1 else -1,
        }

        query += """
            GROUP BY
                product_template.default_code,
                product_template.id  ,
                product_template.name,
                product_pricelist.id,
                product_pricelist.name,
                product_category.id,
                product_category.name
            ORDER BY
                product_template.name,
                 product_pricelist.name
        """

        # Ejecutar la consulta
        wizard.env.cr.execute(query, params)
        result = wizard.env.cr.fetchall()
        averageSales = []
        for row in result:
            referencia = row[0]
            productId = row[1]
            nombre = row[2]
            priceListId = row[3]
            priceListName = row[4]
            categoryId = row[5]
            categoryName = row[6]

            # Obtener los nombres de los productos de la categoría especificada
            product_names = (
                wizard.env["product.template"]
                .search([("id", "=", productId)])
                .mapped("standard_price")
            )  # Cambia 'name' por el campo que necesites
            costo = product_names[0] if len(product_names) > 0 else 0
            gasto = (
                round(costo * (expense_percentage / 100), 2)
                if expense_percentage
                else 0
            )

            costo_neto = round(costo + gasto, 2)
            averageSales.append(
                {
                    "referencia": referencia,
                    "productId": productId,
                    "nombre": nombre,
                    "priceListId": priceListId,
                    "priceListName": priceListName,
                    "categoryId": categoryId,
                    "categoryName": categoryName,
                    "costo": costo,
                    "gasto": gasto,
                    "costo_neto": costo_neto,
                    "barra": gasto,
                }
            )
        # Obtener la fecha actual
        current_date = datetime.now().strftime("%d/%m/%Y")  # Formato de fecha
        bodyreport = {
            "expense_percentage": expense_percentage,
            "date": current_date,
            "averageSales": averageSales,
        }

        # return json.dumps(bodyreport)
        return bodyreport
