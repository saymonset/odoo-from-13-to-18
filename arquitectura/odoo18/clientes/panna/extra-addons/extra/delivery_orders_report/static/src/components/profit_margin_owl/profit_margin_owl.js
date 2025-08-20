/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";
import { getDefaultConfig } from "@web/views/view";
import { Layout } from "@web/search/layout";
import { useSubEnv, reactive, onWillStart, useState } from "@odoo/owl";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { useService } from "@web/core/utils/hooks";
import { ColumnProgress } from "@delivery_orders_report/components/ColumnProgress/ColumnProgress";

export class ProfitMarginOwl extends Component {
  static template = "delivery_orders_report.profit_margin_owl";
  static components = { Layout, ColumnProgress };
  static props = {
    ...standardFieldProps,
  };

  setup() {
    super.setup();
    this.actionService = useService("action");
    useSubEnv({
      config: {
        ...getDefaultConfig(),
        ...this.env.config,
      },
    });

    this.state = useState({
      pricelist: [], // Inicializar pricelist como un array vacío
      selectedPricelist: null,
      categories: [],
      products: [],
      showCatgories: false,
      groupData: "Grupo 1",
      progressValue: 75, // Porcentaje de progreso
      aggregateValue: "75% completado",
    });
    onWillStart(async () => {
      let userCompanyInfo = await this.getInfoUserCompanyService();
      const { company } = userCompanyInfo;
      let priceList = await this.getListPriceService(company?.company_id);
      const { result } = priceList;
      try {
        this.state.pricelist = JSON.parse(result);
      } catch (error) {
        this.state.pricelist = result;
      }
    });
  }

  handleClick(group) {
    console.log("Barra clickeada:", group);
  }

  // Función para obtener un producto por ID
  getProductById(productId) {
    console.log("Hola mundo productId = " + productId);
    let prod = this.state.products.find(
      (product) => product.productId === productId,
    );
    return prod ? prod.margin_percentage : null; // Asegúrate de manejar el caso donde el producto no se encuentra
  }

  // Función para manejar el clic y mostrar el ID en la consola
  async setSearchContext(pricelistId) {
    // Marcamios como activa la pestana
    const updatedPricelist = this.state.pricelist.map((pricelist) => {
      return {
        ...pricelist, // Copia todas las propiedades del objeto original
        isActive: pricelist.productPricelistId === pricelistId, // Establece isActive en true o false
      };
    });
    this.state.pricelist = updatedPricelist;
    // Aquí puedes agregar más lógica si es necesario
    this.state.products = [];
    this.state.categories = [];
    let catego = await this.getCategoriesService(pricelistId);
    this.state.showCategories = false;
    const { result } = catego;
    if (result && result.length > 0) {
      this.state.showCategories = true;
    }
    try {
      this.state.categories = JSON.parse(result);
    } catch (error) {
      this.state.categories = result;
    }
  }
  async searchProductByCategory(categId) {
    // Aquí puedes agregar más lógica si es necesario
    this.state.products = []; //await this.loadCategorieslistData(pricelistId);
    let obj = await this.getProductByCategIdService(categId);
    const { result } = obj;

    try {
      this.state.products = JSON.parse(result);
    } catch (error) {
      this.state.products = result;
    }
  }

  async getCategoriesService(pricelistId) {
    console.log(
      "Llamando al servicio para obtener categorías de entrega con ID de lista de precios:",
      pricelistId,
    );
    this.state.categories = [
      {
        productPricelistId: -1,
        productPricelistName: "",
        productCategoryId: -1,
        productCategoryName: "",
      },
    ];
    try {
      const requestBody = {
        jsonrpc: "2.0",
        params: {
          limit: "12", // Puedes ajustar el límite según sea necesario
          pricelistId: pricelistId,
        },
      };
      const response = await fetch(
        "/delivery_orders_report/order_group_by_categ",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRF-Token": odoo.csrf_token, // Asegúrate de incluir el token CSRF si es necesario
          },
          body: JSON.stringify(requestBody),
        },
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json(); // Analizar la respuesta JSON
      return data; // Retornar los datos recibidos
    } catch (error) {
      console.error("Error al obtener las categorías de entrega:", error);
      return []; // Retornar un array vacío en caso de error
    }
  }

  async getInfoUserCompanyService() {
    try {
      const requestBody = {
        jsonrpc: "2.0",
        method: "call",
        params: {
          args: [],
        },
      };
      const response = await fetch("/delivery_orders_report/user_company", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRF-Token": odoo.csrf_token, // Asegúrate de incluir el token CSRF si es necesario
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json(); // Analizar la respuesta JSON
      const { result } = data;
      return result;
    } catch (error) {
      console.error("Error al obtener las categorías de entrega:", error);
      return []; // Retornar un array vacío en caso de error
    }
  }

  async getListPriceService(companyId = 1) {
    try {
      const requestBody = {
        jsonrpc: "2.0",
        params: {
          limit: "12", // Puedes ajustar el límite según sea necesario
          companyId,
        },
      };
      const response = await fetch("/delivery_orders_report/get_price_list", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRF-Token": odoo.csrf_token, // Asegúrate de incluir el token CSRF si es necesario
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json(); // Analizar la respuesta JSON
      return data; // Retornar los datos recibidos
    } catch (error) {
      console.error("Error al obtener las categorías de entrega:", error);
      return []; // Retornar un array vacío en caso de error
    }
  }

  async getProductByCategIdService(categId = 1) {
    try {
      const requestBody = {
        jsonrpc: "2.0",
        params: {
          limit: "12", // Puedes ajustar el límite según sea necesario
          categId,
        },
      };
      const response = await fetch(
        "/delivery_orders_report/get_product_by_ctegory",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRF-Token": odoo.csrf_token, // Asegúrate de incluir el token CSRF si es necesario
          },
          body: JSON.stringify(requestBody),
        },
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json(); // Analizar la respuesta JSON
      return data; // Retornar los datos recibidos
    } catch (error) {
      console.error("Error al obtener las categorías de entrega:", error);
      return []; // Retornar un array vacío en caso de error
    }
  }

  async _onPrintReport() {
    try {
      const orm = this.env.services.orm;
      const products = this.state.products;

      if (!products || products.length === 0) {
        console.error("No hay productos disponibles para generar el reporte.");
        return;
      }

      const wizardId = await orm.call("profit_margin", "create_report", [
        products,
      ]);

      if (!wizardId) {
        console.error("No se pudo crear el wizard. wizardId es undefined.");
        return;
      }

      console.log({ products });

      const action = await orm.call("profit_margin", "print_report", [
        wizardId,
      ]);

      if (!action) {
        console.error("No se pudo obtener el action para imprimir el reporte.");
        return;
      }

      console.log({ action });
      this.actionService.doAction(action);
    } catch (error) {
      console.error("Error al generar el reporte:", error);
    }
  }
}
// Register as a field widget
registry
  .category("actions")
  .add("delivery_orders_report.profit_margin_owl", ProfitMarginOwl);
