// Placeholder golf-accessory catalogue. No sizes — accessories are one size.
// `images` is intentionally empty: supply real photography later
// (first = primary, second = hover image).

export const categories = ['All', 'Headcovers', 'Headwear', 'Bags', 'Balls & Tees', 'On-Course']

// Product colourways (fixed — independent of the site palette)
export const colors = [
  { name: 'Fairway', hex: '#1f5a3d' },
  { name: 'White', hex: '#f4f4ef' },
  { name: 'Navy', hex: '#1a2a44' },
  { name: 'Lime', hex: '#cdf03a' },
  { name: 'Coral', hex: '#ff7a5c' },
  { name: 'Sky', hex: '#8fcdf5' },
]

const base = [
  ['Driver Headcover', 'Headcovers', 85, ['Fairway', 'White', 'Coral'], 'New'],
  ['Fairway Wood Headcover', 'Headcovers', 75, ['Fairway', 'Navy']],
  ['Blade Putter Cover', 'Headcovers', 65, ['White', 'Lime'], 'Limited'],
  ['Tour Cap', 'Headwear', 42, ['White', 'Navy', 'Sky', 'Lime']],
  ['Mallet Putter Cover', 'Headcovers', 70, ['Navy', 'Coral']],
  ['Stand Bag', 'Bags', 340, ['White', 'Fairway'], 'New'],
  ['Caddie Towel', 'On-Course', 38, ['Fairway', 'White', 'Sky']],
  ['Tour Ball — Dozen', 'Balls & Tees', 54, ['White', 'Lime']],
  ['Bucket Hat', 'Headwear', 48, ['Sky', 'White']],
  ['Sunday Carry Bag', 'Bags', 220, ['Navy', 'Coral'], 'Limited'],
  ['Ball Marker Set', 'On-Course', 28, ['Fairway', 'Coral']],
  ['Wooden Tee Pack', 'Balls & Tees', 14, ['White', 'Lime', 'Coral']],
  ['Iron Cover Set', 'Headcovers', 95, ['Fairway', 'White']],
  ['Performance Visor', 'Headwear', 36, ['White', 'Navy'], 'New'],
  ['Divot Repair Tool', 'On-Course', 32, ['Navy', 'Lime']],
  ['Valuables Pouch', 'Bags', 45, ['Fairway', 'Sky']],
]

export const products = base.map(([name, category, price, colorNames, badge], i) => ({
  id: `p${i + 1}`,
  name,
  category,
  price,
  colors: colorNames,
  badge: badge ?? null,
  images: [],
  order: i,
}))
