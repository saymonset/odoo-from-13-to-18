import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";

patch(PosStore.prototype, {
  get idleTimeout() {
    return [
      {
        timeout: 300000, // 5 minutes(300000)
        action: () =>
          this.mainScreen.component.name !== "PaymentScreen" &&
          this.showScreen("SaverScreen", { config: this.config }),
      },
      {
        timeout: 120000, // 2 minutes
        action: () =>
          this.mainScreen.component.name === "LoginScreen" &&
          this.showScreen("SaverScreen", { config: this.config }),
      },
    ];
  },
});
