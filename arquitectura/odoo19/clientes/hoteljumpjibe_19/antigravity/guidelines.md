# Guía de estilo para el sitio web del Hotel Jump'n Jibe (Odoo 19)

Este documento define la identidad visual que se debe aplicar en el sitio web construido con Odoo Community 19 para el Hotel Jump'n Jibe, ubicado en Playa El Yaque, Isla de Margarita.

## 1. Paleta de colores (usar exactamente estos valores)

| Color             | Código   | Uso principal en Odoo                                                                                 |
|-------------------|----------|-------------------------------------------------------------------------------------------------------|
| **Nordic**        | #19322F  | Texto principal, encabezados, fondo de la barra de navegación, pie de página.                         |
| **Mosque**        | #006655  | Botones primarios (reservar, consultar), enlaces destacados, iconos de acento.                         |
| **Hint of Green** | #D9ECC8  | Fondo de tarjetas destacadas (testimonios, ofertas especiales), secciones promocionales.                |
| **Clear Day**     | #EEF6F6  | Fondo general de las páginas.                                                                          |

### Cómo aplicar los colores en Odoo

#### Opción 1: Personalización del tema
1. Ve a *Sitio web → Configuración → Personalizar*.
2. En la pestaña "Colores", define:
   - Color principal → `#19322F`
   - Color de acento → `#006655`
   - Color de fondo → `#EEF6F6`
3. Guarda los cambios.

#### Opción 2: CSS personalizado (si necesitas más control)
Agrega este código en un bloque "Código personalizado" (HTML/CSS) en cualquier página, o créalo como un adjunto CSS desde el modo técnico.

```css
:root {
  --nordic: #19322F;
  --mosque: #006655;
  --hint-of-green: #D9ECC8;
  --clear-day: #EEF6F6;
}

body {
  background-color: var(--clear-day);
  color: var(--nordic);
}

.btn-primary {
  background-color: var(--mosque) !important;
  border-color: var(--mosque) !important;
  color: white !important;
}

.navbar {
  background-color: var(--nordic) !important;
}

.card-highlight {
  background-color: var(--hint-of-green) !important;
}
2. Tipografía
Fuente obligatoria: SF Pro Display.

Cómo incluirla en Odoo:

Agrega el siguiente código en un bloque "Código personalizado" (HTML/CSS) para importar la fuente desde un CDN (verificar licencia de uso):

css
@import url('https://fonts.cdnfonts.com/css/sf-pro-display');

* {
  font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif !important;
}
Si el CDN no está disponible o no se permite su uso, elige una fuente similar de Google Fonts (por ejemplo, Inter o Montserrat) y ajústala con el equipo de diseño.

3. Principios de diseño y reutilización de componentes
Crea snippets (fragmentos) reutilizables para elementos que se repitan en varias páginas:

Tarjeta de habitación: imagen, título, características, precio, botón "Ver más".

Tarjeta testimonial: texto, nombre del cliente, calificación (opcional).

Botón primario con estilo Mosque.

Encabezado de sección con título en Nordic y posible subtítulo.

Organización de recursos:

Las imágenes se encuentran en la ruta local:
arquitectura/odoo19/clientes/integraiadev_delete19/antigravity/resources/livianas-photos/

Los textos de ejemplo y contenido base están en:
arquitectura/odoo19/clientes/integraiadev_delete19/antigravity/resources/hotel_jump_n_jibe_inicio/

Durante la construcción del sitio, sube las imágenes a la biblioteca de Odoo (Sitio web → Contenido → Imágenes) y organízalas en álbumes (ej: "Habitaciones", "Hotel", "Playa").

Jerarquía de páginas sugerida:

Inicio (Home)

Habitaciones (Rooms)

Ubicación (Location)

Reseñas (Reviews)

Contacto / Reservas (opcional)

Responsive: Prueba el sitio en diferentes dispositivos usando el simulador de Odoo.

4. Mantenimiento
Documenta los snippets personalizados en un archivo aparte (por ejemplo, SNIPPETS.md).

Antes de instalar módulos adicionales (como reservas), consulta con el equipo.