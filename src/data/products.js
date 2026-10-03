// Placeholder catalogue. `images` is intentionally empty — supply real
// product photography later (first = primary, second = hover image).

export const categories = ['All', 'Tops', 'Bottoms', 'Outerwear', 'Accessories']

export const sizes = ['XS', 'S', 'M', 'L', 'XL']

export const colors = [
  { name: 'Ink', hex: '#1b1a17' },
  { name: 'Bone', hex: '#e7e0d0' },
  { name: 'Oxblood', hex: '#7a2e1f' },
  { name: 'Moss', hex: '#5b6148' },
  { name: 'Slate', hex: '#5d6670' },
]

const base = [
  ['Distance Singlet', 'Tops', 68, ['Ink', 'Bone'], 'New'],
  ['Long Run Tee', 'Tops', 82, ['Bone', 'Slate', 'Moss']],
  ['Tempo Short 5"', 'Bottoms', 88, ['Ink', 'Oxblood'], 'New'],
  ['Merino Half Zip', 'Tops', 165, ['Moss', 'Ink']],
  ['Shell Jacket', 'Outerwear', 245, ['Slate', 'Ink'], 'Limited'],
  ['Race Tight', 'Bottoms', 120, ['Ink']],
  ['Lightweight Cap', 'Accessories', 42, ['Bone', 'Ink', 'Oxblood']],
  ['Trail Short 7"', 'Bottoms', 95, ['Moss', 'Slate']],
  ['Thermal Long Sleeve', 'Tops', 110, ['Oxblood', 'Bone']],
  ['Packable Vest', 'Outerwear', 180, ['Ink', 'Moss'], 'New'],
  ['Running Sock — 3 Pack', 'Accessories', 36, ['Bone', 'Ink']],
  ['Track Pant', 'Bottoms', 140, ['Slate', 'Ink']],
  ['Mesh Tank', 'Tops', 64, ['Bone']],
  ['Winter Gloves', 'Accessories', 48, ['Ink']],
  ['Rain Anorak', 'Outerwear', 265, ['Oxblood', 'Slate']],
  ['Split Short 3"', 'Bottoms', 78, ['Ink', 'Bone'], 'Limited'],
]

export const products = base.map(([name, category, price, colorNames, badge], i) => ({
  id: `p${i + 1}`,
  name,
  category,
  price,
  colors: colorNames,
  sizes: category === 'Accessories' ? ['One Size'] : sizes,
  badge: badge ?? null,
  images: [],
  order: i,
}))
