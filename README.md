# UI_Design

Divot & Co — golf accessories product listing page (PLP) — Vite + React + Tailwind CSS v4.

Style direction: premium sport. Expanded heavy uppercase headlines (Archivo), tiny tracked
mono labels, rounded image wells, pill buttons, a scrolling accent marquee and a youthful
palette. Calm editorial pacing and a clear conversion path (sticky filters, one-tap add).

Palette: "Sunset Coral" (warm paper, forest green, coral accent) — tokens in `src/index.css`.
Fonts are self-hosted via `@fontsource-variable` (Archivo, Inter Tight, JetBrains Mono).

Logo concepts: run the dev server and open http://localhost:5173/logos.html
(`src/components/brand/`). Chosen logo: concept 01 "Ball O" (`Logo.jsx`).

Social avatars: ready-to-upload 1080×1080 PNGs in `brand/social/`; preview at
http://localhost:5173/social.html (artwork stays inside the circular crop).

```bash
npm install
npm run dev
```

## Structure

| File | Role |
|---|---|
| `src/index.css` | Design tokens (Sunset Coral) — re-skin here |
| `src/data/products.js` | Placeholder catalogue; `images: []` is where product photos go |
| `src/components/ImageSlot.jsx` | Renders an image, or a hatched placeholder with its aspect ratio |
| `src/components/Header.jsx` | Announcement bar, sticky header, mobile menu |
| `src/components/CollectionHero.jsx` | Breadcrumb + oversized collection title |
| `src/components/Toolbar.jsx` | Sticky category tabs, grid density, sort, filter trigger |
| `src/components/ProductCard.jsx` | Image + hover image, badge, one-tap add, selectable colourways |
| `src/components/Marquee.jsx` | Scrolling accent band |
| `src/components/brand/Marks.jsx` | Logo concepts (wordmarks, icons, crest) |
| `src/components/brand/LogoConcepts.jsx` | Logo comparison page (`logos.html`) |
| `src/components/EditorialTile.jsx` | Story tile that interrupts the grid |
| `src/components/FilterDrawer.jsx` | Colour / price filters |
| `src/components/StorySplit.jsx`, `Newsletter.jsx`, `Footer.jsx` | Brand sections |

## Adding product images

Put files in `public/products/` and reference them in `src/data/products.js`:

```js
images: ['/products/driver-cover-front.jpg', '/products/driver-cover-back.jpg']
```

The first image is the primary, the second crossfades in on hover. Placeholders use a 4:5 ratio.
