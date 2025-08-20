from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _process_pos_ui_product_product(self, products, config_id):
        config = config_id
        warehouse_id = (
            config.picking_type_id.warehouse_id.id if config.picking_type_id else False
        )

        for product in products:
            product_rec = self.env["product.product"].browse(product["id"])
            if warehouse_id and config.hide_unavailable_product:
                # Check stock availability in the warehouse linked to the picking type
                stock_quant = self.env["stock.quant"].search(
                    [
                        ("product_id", "=", product_rec.id),
                        (
                            "location_id",
                            "child_of",
                            config.picking_type_id.default_location_src_id.id,
                        ),
                    ],
                    limit=1,
                )
                product["is_available"] = (
                    stock_quant.quantity > 0 if stock_quant else False
                )
            else:
                product["is_available"] = True

        return super()._process_pos_ui_product_product(products, config_id)
