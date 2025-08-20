from odoo import fields, models


class pos_config(models.Model):
    _inherit = "pos.config"

    allow_large_text = fields.Boolean(
        "Allow large text",
        help="Allows you to show product name large text when there is no product image.",
    )
    product_block_width = fields.Integer("Product Block Width(px)", default=140)
    product_block_height = fields.Integer("Product Block Height(px)", default=115)
    text_font_size = fields.Integer("Text Font Size(px)", default=25)


class product_product(models.Model):
    _inherit = "product.product"

    product_has_image = fields.Boolean(compute="_compute_has_image", string="Has Image")

    def _compute_has_image(self):
        for product in self:
            if product.image_1920:
                product.product_has_image = True
            else:
                product.product_has_image = False
