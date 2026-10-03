import { useEffect, useState } from 'react'
import { CloseIcon, PlusIcon } from './Icons'
import { colors, sizes } from '../data/products'

export const priceRanges = [
  { id: 'u75', label: 'Under $75', test: (p) => p < 75 },
  { id: '75-150', label: '$75 – $150', test: (p) => p >= 75 && p <= 150 },
  { id: 'o150', label: 'Over $150', test: (p) => p > 150 },
]

function Section({ title, children, defaultOpen = true }) {
  const [open, setOpen] = useState(defaultOpen)
  return (
    <div className="border-b border-line py-5">
      <button className="flex w-full items-center justify-between" onClick={() => setOpen(!open)}>
        <span className="eyebrow">{title}</span>
        <PlusIcon className={`transition-transform duration-500 ease-soft ${open ? 'rotate-45' : ''}`} />
      </button>
      <div className={`grid transition-[grid-template-rows] duration-500 ease-soft ${open ? 'grid-rows-[1fr]' : 'grid-rows-[0fr]'}`}>
        <div className="overflow-hidden"><div className="pt-4">{children}</div></div>
      </div>
    </div>
  )
}

const toggle = (list, v) => (list.includes(v) ? list.filter((x) => x !== v) : [...list, v])

export default function FilterDrawer({ open, onClose, filters, onChange, resultCount }) {
  useEffect(() => {
    const onKey = (e) => e.key === 'Escape' && onClose()
    window.addEventListener('keydown', onKey)
    document.body.style.overflow = open ? 'hidden' : ''
    return () => window.removeEventListener('keydown', onKey)
  }, [open, onClose])

  return (
    <div className={`fixed inset-0 z-50 ${open ? '' : 'pointer-events-none'}`} aria-hidden={!open}>
      <div className={`absolute inset-0 bg-ink/30 transition-opacity duration-500 ${open ? 'opacity-100' : 'opacity-0'}`} onClick={onClose} />
      <aside
        className={`absolute inset-y-0 right-0 flex w-full max-w-md flex-col bg-paper transition-transform duration-500 ease-soft ${
          open ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        <div className="flex h-16 items-center justify-between border-b border-line px-6">
          <h2 className="font-serif text-2xl">Filter</h2>
          <button aria-label="Close filters" onClick={onClose}><CloseIcon /></button>
        </div>

        <div className="flex-1 overflow-y-auto px-6">
          <Section title="Size">
            <div className="grid grid-cols-5 gap-2">
              {sizes.map((s) => (
                <button
                  key={s}
                  onClick={() => onChange({ ...filters, sizes: toggle(filters.sizes, s) })}
                  className={`border py-2.5 text-[13px] transition-colors ${
                    filters.sizes.includes(s) ? 'border-ink bg-ink text-paper' : 'border-line hover:border-ink'
                  }`}
                >
                  {s}
                </button>
              ))}
            </div>
          </Section>

          <Section title="Colour">
            <div className="flex flex-wrap gap-x-5 gap-y-3">
              {colors.map((c) => {
                const on = filters.colors.includes(c.name)
                return (
                  <button
                    key={c.name}
                    onClick={() => onChange({ ...filters, colors: toggle(filters.colors, c.name) })}
                    className="flex items-center gap-2 text-[13px]"
                  >
                    <span
                      className={`h-5 w-5 rounded-full ring-1 ring-offset-2 ring-offset-paper transition-all ${on ? 'ring-ink' : 'ring-ink/15'}`}
                      style={{ background: c.hex }}
                    />
                    <span className={on ? 'text-ink' : 'text-ink-2'}>{c.name}</span>
                  </button>
                )
              })}
            </div>
          </Section>

          <Section title="Price">
            <div className="space-y-3">
              {priceRanges.map((r) => (
                <label key={r.id} className="flex cursor-pointer items-center gap-3 text-[14px]">
                  <input
                    type="checkbox"
                    checked={filters.prices.includes(r.id)}
                    onChange={() => onChange({ ...filters, prices: toggle(filters.prices, r.id) })}
                    className="h-4 w-4 accent-ink"
                  />
                  {r.label}
                </label>
              ))}
            </div>
          </Section>
        </div>

        <div className="grid grid-cols-2 gap-3 border-t border-line p-6">
          <button
            onClick={() => onChange({ sizes: [], colors: [], prices: [] })}
            className="eyebrow border border-line py-3.5 transition-colors hover:border-ink"
          >
            Clear all
          </button>
          <button onClick={onClose} className="eyebrow bg-ink py-3.5 text-paper transition-colors hover:bg-accent">
            Show {resultCount} items
          </button>
        </div>
      </aside>
    </div>
  )
}
