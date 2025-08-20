import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { useBarcodeReader } from "@point_of_sale/app/barcode/barcode_reader_hook";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";

patch(ProductScreen.prototype, {
  setup() {
    super.setup(...arguments);
    if (this.pos.config.pos_category_id) {
      if (!this.pos.selectedCategory) {
        this.pos.setSelectedCategory(this.pos.config.pos_category_id.id);
      }
      if (this.pos.selectedCategory) {
        if (
          this.pos.config.pos_category_id.id != this.pos.selectedCategory.id
        ) {
          this.pos.setSelectedCategory(this.pos.config.pos_category_id.id);
        }
      }
    }
  },
});

// patch(PosStore.prototype, {
//     setSelectedCategory(categoryId) {
//         if (categoryId === this.selectedCategory?.id) {
//             if (this.selectedCategory.parent_id) {
//                 this.selectedCategory = this.selectedCategory.parent_id;
//             } else {
//                 this.selectedCategory = this.models["pos.category"].get(categoryId);
//             }
//         } else {
//             this.selectedCategory = this.models["pos.category"].get(categoryId);
//         }
//     },
//     // createNewOrder() {
//     //     const order = super.createNewOrder(...arguments);
//     //     if (this.config.pos_category_id) {
//     //         this.setSelectedCategory(this.config.pos_category_id.id)
//     //     }
//     //     return order;
//     // },
// });

// patch(PosOrder.prototype, {
//     setup() {
//         super.setup(...arguments);
//         if(this.config.default_partner_id && !this.partner_id && !this.uiState.locked){
//             this.update({ partner_id: this.config.default_partner_id });
//         }
//     },
// });
