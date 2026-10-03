# UI_Design

Product listing page (PLP) template — Vite + React + Tailwind CSS v4.

Style direction: editorial skeleton from Aesop / Tracksmith (warm paper palette, serif
headlines, split layouts, generous whitespace), typographic tension from Satisfy (oversized
serif vs. tiny tracked mono labels), and the clear conversion structure of Shopify / Cohere
(sticky filter bar, quick add, strong CTAs).

```bash
npm install
npm run dev
```

## Structure

| File | Role |
|---|---|
| `src/index.css` | Design tokens (colours, fonts, easing) — re-skin here |
| `src/data/products.js` | Placeholder catalogue; `images: []` is where product photos go |
| `src/components/ImageSlot.jsx` | Renders an image, or a hatched placeholder with its aspect ratio |
| `src/components/Header.jsx` | Announcement bar, sticky header, mobile menu |
| `src/components/CollectionHero.jsx` | Breadcrumb + oversized collection title |
| `src/components/Toolbar.jsx` | Sticky category tabs, grid density, sort, filter trigger |
| `src/components/ProductCard.jsx` | Image + hover image, badge, quick-add sizes, swatches |
| `src/components/EditorialTile.jsx` | Story tile that interrupts the grid |
| `src/components/FilterDrawer.jsx` | Size / colour / price filters |
| `src/components/StorySplit.jsx`, `Newsletter.jsx`, `Footer.jsx` | Brand sections |

## Adding product images

Put files in `public/products/` and reference them in `src/data/products.js`:

```js
images: ['/products/singlet-front.jpg', '/products/singlet-back.jpg']
```

The first image is the primary, the second crossfades in on hover. Placeholders use a 4:5 ratio.
