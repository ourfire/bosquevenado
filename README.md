# Bosque Venado

Sitio de Bosque Venado: comunidad neorural en el tablaje 3735 (Seyé, junto a Acanceh, Yucatán). Predio de 7 ha; la etapa 3, de 3 ha, es la que está a la venta en clusters de 2, 4 y 8 lotes de 200 m².

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

Edita `estado.json` (no hace falta volver a construir el sitio). Se puede marcar por lote o por cluster completo (por su letra):

```json
{"actualizado": "2026-11-11", "lotes": {"23": "vendido"}, "clusters": {"C": "apartado"}}
```

Lo que no aparece está disponible. El precio de preventa sube 5% por cada 4 lotes marcados como `vendido`; el cotizador y el PDF lo calculan solos.

## Seguridad

- `netlify.toml` define encabezados de seguridad (CSP, HSTS, sin iframes, sin cámara ni ubicación).
- El sitio no carga código de terceros: jsPDF vive en `vendor/` (licencia MIT en `vendor/jspdf-LICENSE`). Solo las fuentes vienen de Google Fonts.
- El sitio no cobra ni pide datos de pago. Los pagos se hacen solo a las cuentas que diga el contrato.

## Cómo trabajamos

- `preview`: rama de trabajo. Cada push genera un branch deploy en Netlify (0 créditos).
- `main`: producción. Solo se hace merge cuando el diseño está aprobado (15 créditos por publicación).

## Antes de lanzar

- Quitar `<meta name="robots" content="noindex, nofollow">` de `src/template.html` y de las páginas de gracias.
- Llenar los campos marcados `.tbd` (se ven resaltados en amarillo).
- Apuntar el dominio bosquevenado.com a Netlify (ya están las etiquetas canonical y Open Graph con ese dominio).
- Activar la detección de formularios en Netlify (Forms > Enable form detection) y las notificaciones por correo.
