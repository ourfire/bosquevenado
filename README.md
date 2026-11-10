# Bosque Venado

Sitio de Bosque Venado: cinco hectáreas de monte en Acanceh, Yucatán.

HTML estático, sin build. Formulario de visita con Netlify Forms.

## Cómo trabajamos

- `preview`: rama de trabajo. Cada push genera un branch deploy en Netlify (0 créditos).
- `main`: producción. Solo se hace merge cuando el diseño está aprobado (15 créditos por publicación).

## Antes de lanzar

- Quitar `<meta name="robots" content="noindex, nofollow">` de `index.html` y `gracias.html`.
- Quitar el aviso de borrador y llenar todos los campos marcados `.tbd`.
- Activar la detección de formularios en Netlify (Forms > Enable form detection).
