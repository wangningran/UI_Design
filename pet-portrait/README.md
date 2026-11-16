# Strata — Layered Acrylic Pet Portraits (sample site)

Sample landing page for a studio that hand-scratches pet portraits into stacked sheets of black and clear acrylic.
Single page: `index.html` (inline CSS + JS, no build step). Images live in `assets/img/`.

## What moves
- **Hero**: the portrait's acrylic sheets drop in one by one (back panel, fur layer, face layer, front sheet), then float apart slightly and follow the pointer. Scrolling pulls the sheets further apart.
- **Anatomy of a portrait**: a pinned scroll section. The framed piece explodes into its six layers, steps through each one (the list on the left follows), then reassembles face-on.
- **Selected works**: images reveal on scroll; a ×3 loupe follows the cursor so you can see the scratches.

## Design
Cool light grey and black, one typeface (Inter Tight), thin rules, lots of whitespace, English copy.

## Placeholders to replace
- Studio name, prices, lead times, contact details.
- The order form does not submit anywhere yet.
- The face/fur split in the layer effect is a soft oval mask (`--cx --cy --rx --ry` on each `.stack`). For real pieces, use separate photos of each layer.
