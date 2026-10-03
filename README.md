# UI_Design

Golf accessories product listing page (PLP) — Vite + React + Tailwind CSS v4.

Style direction: premium sport. Expanded heavy uppercase headlines (Archivo), tiny tracked
mono labels, rounded image wells, pill buttons, a scrolling accent marquee and a youthful
palette. Calm editorial pacing and a clear conversion path (sticky filters, one-tap add).

Three palettes are defined in `src/index.css` (`fairway`, `sky`, `coral`). The floating
switcher in the bottom-left corner (`ThemeSwitcher.jsx`) is for preview only — remove it
and set `data-theme` in `index.html` once a palette is chosen.

```bash
npm install
npm run dev
```

## Structure

| File | Role |
|---|---|
| `src/index.css` | Design tokens and the three palettes — re-skin here |
| `src/data/products.js` | Placeholder catalogue; `images: []` is where product photos go |
| `src/components/ImageSlot.jsx` | Renders an image, or a hatched placeholder with its aspect ratio |
| `src/components/Header.jsx` | Announcement bar, sticky header, mobile menu |
| `src/components/CollectionHero.jsx` | Breadcrumb + oversized collection title |
| `src/components/Toolbar.jsx` | Sticky category tabs, grid density, sort, filter trigger |
| `src/components/ProductCard.jsx` | Image + hover image, badge, one-tap add, selectable colourways |
| `src/components/Marquee.jsx` | Scrolling accent band |
| `src/components/ThemeSwitcher.jsx` | Preview-only palette switcher |
| `src/components/EditorialTile.jsx` | Story tile that interrupts the grid |
| `src/components/FilterDrawer.jsx` | Colour / price filters |
| `src/components/StorySplit.jsx`, `Newsletter.jsx`, `Footer.jsx` | Brand sections |

## Adding product images

Put files in `public/products/` and reference them in `src/data/products.js`:

```js
images: ['/products/driver-cover-front.jpg', '/products/driver-cover-back.jpg']
```

The first image is the primary, the second crossfades in on hover. Placeholders use a 4:5 ratio.
