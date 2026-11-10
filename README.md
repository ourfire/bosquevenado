# Bosque Venado

Sitio de Bosque Venado: cinco hectáreas de monte en Acanceh, Yucatán.

HTML estático en español (`index.html`) e inglés (`en/index.html`). Formulario de visita con Netlify Forms.

## Editar

Los textos están en `src/build.py`, el diseño en `src/template.html` y el plano en `src/plan.py`
(coordenadas del levantamiento topográfico del tablaje 3735). Después de cambiar algo:

```
python3 src/build.py
```

Para marcar lotes apartados o vendidos, edita `const ESTADO={}` en `src/template.html`, por ejemplo `{7:"apartado",12:"vendido"}`.

## Cómo trabajamos

- `preview`: rama de trabajo. Cada push genera un branch deploy en Netlify (0 créditos).
- `main`: producción. Solo se hace merge cuando el diseño está aprobado (15 créditos por publicación).

## Antes de lanzar

- Quitar `<meta name="robots" content="noindex, nofollow">` de `index.html` y `gracias.html`.
- Quitar el aviso de borrador y llenar todos los campos marcados `.tbd`.
- Activar la detección de formularios en Netlify (Forms > Enable form detection).
