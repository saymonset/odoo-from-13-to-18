
---

### **instructions.md**

```markdown
# Instrucciones para construir el sitio web del Hotel Jump'n Jibe en Odoo 19

Este documento guía el proceso de creación del sitio web del Hotel Jump'n Jibe utilizando Odoo Community 19. Se deben seguir los lineamientos visuales definidos en `guidelines.md` y usar los recursos disponibles en las carpetas indicadas.

## Requisitos previos

- Odoo Community 19 instalado y funcionando.
- Módulo **Website** activado.
- Acceso con permisos de administrador.
- Archivos del proyecto disponibles en:
  - Fotos: `arquitectura/odoo19/clientes/integraiadev_delete19/antigravity/resources/livianas-photos/`
  - Textos base: `arquitectura/odoo19/clientes/integraiadev_delete19/antigravity/resources/hotel_jump_n_jibe_inicio/`

## Paso 1: Configurar colores base

1. Ve a *Sitio web → Configuración → Personalizar*.
2. En "Colores", establece:
   - Color principal: `#19322F`
   - Color de acento: `#006655`
   - Color de fondo: `#EEF6F6`
3. Guarda.

## Paso 2: Aplicar tipografía SF Pro Display

Agrega un bloque "Código personalizado" en cualquier página (o en el pie de página) con el siguiente CSS:

```css
@import url('https://fonts.cdnfonts.com/css/sf-pro-display');
* { font-family: 'SF Pro Display', sans-serif !important; }
Si prefieres hacerlo globalmente, puedes crear un adjunto CSS desde Ajustes → Técnico → Acciones → Adjuntos (activa el modo desarrollador primero).

Paso 3: Crear las páginas principales
Desde Sitio web → Sitio → Páginas → Nueva página, crea:

Inicio (ruta /)

Habitaciones (/habitaciones)

Ubicación (/ubicacion)

Reseñas (/resenas)

Contacto (/contacto) (opcional)

Asigna títulos amigables y publícalas.

Paso 4: Subir imágenes a la biblioteca de Odoo
Ve a Sitio web → Contenido → Imágenes.

Crea álbumes:

"Habitaciones"

"Hotel"

"Playa El Yaque"

"Actividades"

Sube todas las fotos desde arquitectura/odoo19/clientes/integraiadev_delete19/antigravity/resources/livianas-photos/ a los álbumes correspondientes. Usa nombres descriptivos (ej: habitacion-doble-1.jpg).

Paso 5: Crear snippets reutilizables (opcional pero recomendado)
Para ahorrar tiempo, crea snippets personalizados:

Ve a Ajustes → Técnico → Interfaz de usuario → Snippets personalizados.

Crea un snippet llamado "Tarjeta de habitación" con la siguiente estructura HTML (adapta según necesidad):

html
<div class="card" style="border: 1px solid #19322F; border-radius: 8px; overflow: hidden;">
  <img src="URL_IMAGEN" class="card-img-top" alt="Habitación">
  <div class="card-body" style="background-color: #EEF6F6;">
    <h5 class="card-title" style="color: #19322F;">Habitación Deluxe</h5>
    <p class="card-text">Características: cama king, vista al mar, baño privado.</p>
    <p class="card-text" style="color: #006655; font-weight: bold;">$120 por noche</p>
    <a href="#" class="btn btn-primary" style="background-color: #006655; border-color: #006655;">Ver más</a>
  </div>
</div>
Guarda. Luego podrás arrastrar este snippet desde la paleta al editar páginas.

Repite para "Tarjeta testimonial" (fondo #D9ECC8).

Paso 6: Construir la página de inicio
Edita la página de inicio y arma la estructura:

Hero: Bloque de imagen con texto superpuesto. Usa una foto impactante de playa (ej. playa-atardecer.jpg). Agrega un título como "Hotel Jump'n Jibe" y un botón "Reservar ahora" con color Mosque.

Sección introductoria: Título "Bienvenidos al Jump'n Jibe" (color Nordic). Texto extraído de hotel_jump_n_jibe_inicio/bienvenida.txt (o similar). Fondo Clear Day.

Sección de destacados: Tres columnas con tarjetas de fondo Hint of Green. Cada una: ícono (puedes usar FontAwesome de Odoo), título breve (ej. "Frente al mar", "Windsurf", "Ambiente relajado") y descripción corta. Los textos puedes encontrarlos en hotel_jump_n_jibe_inicio/destacados.txt.

Llamado a la acción: Bloque con fondo Mosque y texto blanco, botón "Ver habitaciones" que enlace a /habitaciones.

Paso 7: Página de Habitaciones
Título principal: "Nuestras habitaciones" (H2, color Nordic).

Cuadrícula de columnas (2 o 3 por fila). En cada columna, inserta el snippet "Tarjeta de habitación" y personaliza:

Imagen: selecciona la correspondiente del álbum "Habitaciones".

Título y descripción: usa los textos de hotel_jump_n_jibe_inicio/habitaciones/ (puede haber un archivo por tipo de habitación).

Precio: según tarifas.

Botón "Reservar" que puede llevar a un formulario de contacto o a un motor externo.

Paso 8: Página de Ubicación
Título: "La mejor playa para windsurf y kitesurf" (color Nordic).

Dos columnas:

Columna izquierda: Texto descriptivo de Playa El Yaque, extraído de hotel_jump_n_jibe_inicio/ubicacion/playa.txt. Puedes incluir fotos de la playa.

Columna derecha: Bloque "Mapa" de Odoo con la dirección: "Playa El Yaque, Isla de Margarita, Venezuela". Ajusta el zoom para que se vea el hotel.

Añade un carrusel con fotos de la playa desde el álbum "Playa El Yaque".

Paso 9: Página de Reseñas
Título: "Lo que dicen nuestros huéspedes" (color Nordic).

Cuadrícula de columnas. Cada columna: usa el snippet "Tarjeta testimonial" con fondo Hint of Green.

Texto del testimonio: puedes crear algunos ficticios basados en reseñas reales (si hay archivos en hotel_jump_n_jibe_inicio/resenas/, úsalos).

Nombre del cliente.

Calificación con estrellas (puedes usar caracteres ★ y ☆).

Asegúrate de que las tarjetas se vean bien en móviles.

Paso 10: Revisar y ajustar
Previsualiza el sitio en distintos tamaños de pantalla (responsive).

Verifica que los colores y tipografía se apliquen correctamente en todos los elementos.

Comprueba que los botones enlacen a las páginas correctas.

Ajusta márgenes y paddings si es necesario mediante CSS adicional.

Paso 11: SEO y metadatos
Para cada página, haz clic en "Editar" → pestaña "SEO" y completa:

Título para SEO (incluye "Hotel Jump'n Jibe El Yaque")

Descripción meta (atractiva, con palabras clave: "hotel", "playa", "windsurf", "Margarita")

URL amigable (ej. /habitaciones)

Imagen para redes sociales (sube una foto representativa desde la biblioteca)

Paso 12: Publicar y probar
Publica todas las páginas.

Navega por el sitio como un usuario real, probando cada enlace y formulario.

Pide a un compañero que lo revise y dé retroalimentación.

Notas adicionales
Si necesitas un sistema de reservas, evalúa el módulo "Hotel" de Odoo (community) o integra un motor externo mediante iframe (previa consulta).

Las rutas de los recursos son locales; asegúrate de que el equipo tenga acceso a ellas.

Guarda los snippets personalizados y el CSS en un lugar seguro por si necesitas restaurarlos.

text

---

Estos dos archivos (`guidelines.md` e `instructions.md`) están listos para ser entregados al equipo de desarrollo. Contienen toda la información necesaria para construir el sitio web del Hotel Jump'n Jibe en Odoo 19, siguiendo la identidad visual definida y utilizando los recursos proporcionados.