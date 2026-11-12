# Bosque Venado

Sitio de Bosque Venado: comunidad neorural en el tablaje 3735 (Seyé, junto a Acanceh, Yucatán). Predio de 7 ha; la etapa 3, de 2 ha, es la que está a la venta en clusters de 2, 4 y 8 lotes de 200 m².

HTML estático en español (`index.html`) e inglés (`en/index.html`). Formulario de visita con Netlify Forms. Cotizador con descarga en PDF (jsPDF desde cdnjs, se carga solo al pedir el PDF).

## Editar

- Textos: `src/build.py`. Diseño y scripts del cotizador: `src/template.html`.
- Plano: `src/engine.js` (misma geometría que el trazador interactivo; `CONFIG` define calle, clusters y bloques comunes).
- Correo de contacto: constante `CORREO` en `src/build.py` (info@bosquevenado.com).
- Fotos: carpeta `img/` (versiones de 1000 y 1800 px).

Después de cambiar algo (necesita Python 3 y Node):

```
python3 src/build.py
```

## Apartados y vendidos

Edita `estado.json` (no hace falta volver a construir el sitio):

```json
{"actualizado": "2026-11-11", "clusters": {"3": "apartado", "10": "vendido"}}
```

Los clusters que no aparecen están disponibles. El número es el que se ve en el plano.
El precio de preventa sube 5% por cada 4 lotes marcados como `vendido`; el cotizador y el PDF lo calculan solos.

## Cómo trabajamos

- `preview`: rama de trabajo. Cada push genera un branch deploy en Netlify (0 créditos).
- `main`: producción. Solo se hace merge cuando el diseño está aprobado (15 créditos por publicación).

## Antes de lanzar

- Quitar `<meta name="robots" content="noindex, nofollow">` de `src/template.html` y de las páginas de gracias.
- Quitar el aviso de borrador y llenar todos los campos marcados `.tbd`.
- Vaciar los clusters de ejemplo en `estado.json`.
- Apuntar el dominio bosquevenado.com a Netlify (ya están las etiquetas canonical y Open Graph con ese dominio).
- Activar la detección de formularios en Netlify (Forms > Enable form detection) y las notificaciones por correo.
