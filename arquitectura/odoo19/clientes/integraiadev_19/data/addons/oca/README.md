# 📦 Módulos OCA - Odoo 19.0

Este directorio está destinado a contener los módulos de la **Odoo Community Association (OCA)** compatibles con la versión 19.0.

---

## 📂 Ubicación de los Fuentes
Los módulos se encuentran centralizados en la siguiente ruta compartida del sistema:
`📂 /home/odoo/modulos_odoo/shared/oca/19.0`

> [!NOTE]
> Este directorio en el repositorio puede ser un punto de montaje o una referencia a la ubicación compartida para mantener la consistencia entre diferentes entornos de desarrollo.

## 🛠️ Módulos Disponibles (Ejemplos)
Actualmente, el repositorio compartido incluye módulos esenciales como:
- **Contabilidad:** `account_tax_balance`, `account_usability`
- **Recursos Humanos:** `hr_employee_firstname`, `hr_department_code`, `hr_course`
- **Utilidades:** `web_responsive`, `report_xlsx`, `base_technical_features`
- **Localización/Otros:** `partner_statement`, `website_whatsapp`

## 🚀 Cómo añadir nuevos módulos
Para añadir módulos adicionales de la OCA:
1. Clonar el repositorio correspondiente de [GitHub OCA](https://github.com/OCA).
2. Asegurarse de seleccionar la rama `19.0`.
3. Copiar el módulo a la ruta compartida o enlazarlo simbólicamente aquí.

```bash
# Ejemplo:
git clone -b 19.0 --single-branch https://github.com/OCA/web.git
cp -r web/web_responsive /home/odoo/modulos_odoo/shared/oca/19.0/
```

---
*Mantenido por el equipo de IntegraIA*