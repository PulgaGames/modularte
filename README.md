# ModulArt — Landing Page

Landing page estática para **ModulArt**, ebanistería en Ciudad de Panamá.

## Stack

- HTML5 + CSS3 + JavaScript vanilla (sin frameworks)
- Imágenes optimizadas vía Unsplash CDN (`w=`, `q=75`, `srcset`)
- Despliegue recomendado: **Vercel** (CDN global, gratis, sin cold starts)

## Desarrollo local

```bash
npx serve .
```

Abre `http://localhost:3000`

## Desplegar en Vercel (gratis)

1. Sube el repo a GitHub
2. Entra en [vercel.com](https://vercel.com) → **Add New Project**
3. Importa el repositorio
4. Framework Preset: **Other** (sitio estático)
5. Deploy

O con CLI:

```bash
npm i -g vercel
vercel
```

## Personalizar

Actualiza en `index.html` y `js/main.js`:

| Dato | Ubicación |
|------|-----------|
| WhatsApp | `50760000000` en HTML y `WHATSAPP_NUMBER` en `main.js` |
| Email | `info@modulart.pa` |
| Instagram | `@modulart.pa` |
| Dirección exacta | Sección contacto + iframe de Google Maps |

## Rendimiento

- Sin jQuery, sin WordPress, sin sliders pesados
- `preload` en imagen hero
- `loading="lazy"` en imágenes below-the-fold
- Fuentes del sistema (0 requests de fonts)
- CSS/JS < 15 KB combinados
