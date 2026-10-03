import { useState } from 'react'
import ImageSlot from './ImageSlot'
import { PlusIcon } from './Icons'
import { colors as palette } from '../data/products'

const hexOf = (name) => palette.find((c) => c.name === name)?.hex

export default function ProductCard({ product, onAdd }) {
  const [hover, setHover] = useState(false)
  const [colour, setColour] = useState(product.colors[0])
  const [added, setAdded] = useState(false)
  const [primary, secondary] = product.images

  const add = (e) => {
    e.preventDefault()
    onAdd(product, colour)
    setAdded(true)
    setTimeout(() => setAdded(false), 1400)
  }

  return (
    <article className="group" onMouseEnter={() => setHover(true)} onMouseLeave={() => setHover(false)}>
      <a href="#" className="relative block overflow-hidden rounded-xl">
        <ImageSlot src={primary} alt={product.name} />
        {/* Hover image slot — crossfades in when a second image exists */}
        <div className={`absolute inset-0 transition-opacity duration-700 ease-soft ${hover && secondary ? 'opacity-100' : 'opacity-0'}`}>
          {secondary && <ImageSlot src={secondary} alt="" />}
        </div>

        {product.badge && (
          <span
            className={`eyebrow absolute left-3 top-3 rounded-full px-2.5 py-1 ${
              product.badge === 'Limited' ? 'bg-ink text-paper' : 'bg-accent text-on-accent'
            }`}
          >
            {product.badge}
          </span>
        )}

        {/* Quick add — one-tap add of the selected colourway */}
        <button
          onClick={add}
          aria-label={`Add ${product.name} to bag`}
          className={`absolute bottom-3 right-3 flex h-11 items-center gap-2 overflow-hidden rounded-full pl-3.5 pr-3.5 transition-all duration-500 ease-soft ${
            added ? 'bg-accent text-on-accent' : 'bg-paper text-ink hover:bg-ink hover:text-paper'
          } lg:translate-y-2 lg:opacity-0 lg:group-hover:translate-y-0 lg:group-hover:opacity-100`}
        >
          <PlusIcon className={`shrink-0 transition-transform duration-500 ${added ? 'rotate-45' : ''}`} />
          <span className="eyebrow max-w-0 overflow-hidden whitespace-nowrap transition-all duration-500 ease-soft group-hover:max-w-28">
            {added ? 'Added' : 'Add to bag'}
          </span>
        </button>
      </a>

      <div className="mt-4 flex items-start justify-between gap-4">
        <div>
          <p className="eyebrow text-muted">{product.category}</p>
          <h3 className="mt-1.5 text-[15px] font-medium leading-snug">
            <a href="#" className="link-underline">{product.name}</a>
          </h3>
        </div>
        <p className="text-[15px] font-medium tabular-nums">${product.price}</p>
      </div>

      {/* Selectable colourways */}
      <div className="mt-3 flex items-center gap-2">
        {product.colors.map((name) => (
          <button
            key={name}
            title={name}
            aria-label={name}
            onClick={() => setColour(name)}
            className={`h-4 w-4 rounded-full ring-offset-2 ring-offset-paper transition-all duration-300 ${
              colour === name ? 'ring-[1.5px] ring-ink' : 'ring-1 ring-ink/15 hover:ring-ink/40'
            }`}
            style={{ background: hexOf(name) }}
          />
        ))}
        <span className="ml-1 text-[12px] text-muted">{colour}</span>
      </div>
    </article>
  )
}
