// Placeholder golf-accessory catalogue. No sizes — accessories are one size.
// `images` is empty: until real photography is supplied (first = primary,
// second = hover), cards show a vector mock-up drawn by ProductArt.

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
  ['driver', 'Driver Headcover', 'Headcovers', 85, ['Fairway', 'White', 'Coral'], 'New'],
  ['wood', 'Fairway Wood Headcover', 'Headcovers', 75, ['Fairway', 'Navy']],
  ['blade', 'Blade Putter Cover', 'Headcovers', 65, ['White', 'Lime'], 'Limited'],
  ['cap', 'Tour Cap', 'Headwear', 42, ['White', 'Navy', 'Sky', 'Lime']],
  ['mallet', 'Mallet Putter Cover', 'Headcovers', 70, ['Navy', 'Coral']],
  ['standbag', 'Stand Bag', 'Bags', 340, ['White', 'Fairway'], 'New'],
  ['towel', 'Caddie Towel', 'On-Course', 38, ['Fairway', 'White', 'Sky']],
  ['balls', 'Tour Ball — Dozen', 'Balls & Tees', 54, ['White', 'Lime']],
  ['bucket', 'Bucket Hat', 'Headwear', 48, ['Sky', 'White']],
  ['carrybag', 'Sunday Carry Bag', 'Bags', 220, ['Navy', 'Coral'], 'Limited'],
  ['markers', 'Ball Marker Set', 'On-Course', 28, ['Fairway', 'Coral']],
  ['tees', 'Wooden Tee Pack', 'Balls & Tees', 14, ['White', 'Lime', 'Coral']],
  ['irons', 'Iron Cover Set', 'Headcovers', 95, ['Fairway', 'White']],
  ['visor', 'Performance Visor', 'Headwear', 36, ['White', 'Navy'], 'New'],
  ['divot', 'Divot Repair Tool', 'On-Course', 32, ['Navy', 'Lime']],
  ['pouch', 'Valuables Pouch', 'Bags', 45, ['Fairway', 'Sky']],
]

export const products = base.map(([art, name, category, price, colorNames, badge], i) => ({
  id: `p${i + 1}`,
  art, // mock illustration key (components/ProductArt.jsx)
  name,
  category,
  price,
  colors: colorNames,
  badge: badge ?? null,
  images: [],
  order: i,
}))
