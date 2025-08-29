/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";
import { ItemCounter } from "@react-odoo/components/ItemCounter/ItemCounter";
 
 

 

 const itemsInCart2 = [
    { productName: 'xxNintendo Switch 2', quantity: 1 },
    { productName: 'xxPro Controller', quantity: 2 },
    { productName: 'xxSuper Smash', quantity: 5 },
];
export class FirstStepsApp extends Component {
    static components = {  ItemCounter};
    static template = "react-odoo.FirstStepsApp";
    static props = {};

    setup() {
        
          this.itemsInCart2 = itemsInCart2;
    }
}
// Register as a field widget
registry
  .category("actions")
  .add("react-odoo.FirstStepsApp", FirstStepsApp);