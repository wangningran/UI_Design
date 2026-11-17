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

## Layer extraction tool
`tools/extract_layers.py` pulls the individual acrylic sheets out of a video in which the sheets are stacked one by one into the same mat, filmed from above.

```bash
pip install opencv-python-headless numpy        # ffmpeg must also be installed
python3 tools/extract_layers.py scan   video.mp4 out/                       # 1 fps contact sheet with timestamps
python3 tools/extract_layers.py frames video.mp4 out/ --start 34 --end 45   # straighten every frame to the mat window
python3 tools/extract_layers.py split  out/ --states 10,17,40,52,65,81      # one frame per stacking state, bottom first
```

`split` writes `out/layers/1.jpg` (the black back sheet), `2.png … n.png` (transparent sheets, top sheet last), `full.jpg` and a review sheet `out/layers.jpg`.
Use `--lift` (default 28) to make it more or less sensitive for dark fur. Best results come from 4K footage, a fixed camera directly above, and a two-second pause after each sheet.
