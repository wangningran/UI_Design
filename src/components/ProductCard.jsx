import { useState } from 'react'
import ImageSlot from './ImageSlot'
import { colors as palette } from '../data/products'

export default function ProductCard({ product, onAdd }) {
  const [hover, setHover] = useState(false)
  const [added, setAdded] = useState(null)
  const [primary, secondary] = product.images

  const add = (size) => {
    onAdd(product, size)
    setAdded(size)
    setTimeout(() => setAdded(null), 1400)
  }

  return (
    <article className="group" onMouseEnter={() => setHover(true)} onMouseLeave={() => setHover(false)}>
      <a href="#" className="relative block">
        <ImageSlot src={primary} alt={product.name} />
        {/* Hover image slot — crossfades in when a second image exists */}
        <div className={`absolute inset-0 transition-opacity duration-700 ease-soft ${hover && secondary ? 'opacity-100' : 'opacity-0'}`}>
          {secondary && <ImageSlot src={secondary} alt="" />}
        </div>

        {product.badge && (
          <span className={`eyebrow absolute left-3 top-3 px-2 py-1 ${product.badge === 'Limited' ? 'bg-accent text-paper' : 'bg-paper text-ink'}`}>
            {product.badge}
          </span>
        )}

        {/* Quick add — slides up on hover (desktop) */}
        <div
          className="absolute inset-x-3 bottom-3 translate-y-2 bg-paper/95 p-3 opacity-0 backdrop-blur transition-all duration-500 ease-soft group-hover:translate-y-0 group-hover:opacity-100 max-lg:hidden"
          onClick={(e) => e.preventDefault()}
        >
          <p className="eyebrow mb-2 text-muted">{added ? `Added — ${added}` : 'Quick add'}</p>
          <div className="flex flex-wrap gap-1.5">
            {product.sizes.map((s) => (
              <button
                key={s}
                onClick={() => add(s)}
                className={`min-w-9 border px-2 py-1.5 text-[12px] transition-colors ${
                  added === s ? 'border-ink bg-ink text-paper' : 'border-line hover:border-ink'
                }`}
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      </a>

      <div className="mt-3.5 flex items-start justify-between gap-4">
        <div>
          <h3 className="text-[14px] leading-snug">
            <a href="#" className="link-underline">{product.name}</a>
          </h3>
          <p className="mt-1 text-[13px] text-muted">
            {product.colors.length} {product.colors.length === 1 ? 'colour' : 'colours'}
          </p>
        </div>
        <p className="text-[14px] tabular-nums">${product.price}</p>
      </div>

      <div className="mt-2.5 flex gap-1.5">
        {product.colors.map((name) => (
          <span
            key={name}
            title={name}
            className="h-3 w-3 rounded-full ring-1 ring-ink/15 ring-offset-1 ring-offset-paper"
            style={{ background: palette.find((c) => c.name === name)?.hex }}
          />
        ))}
      </div>
    </article>
  )
}
