import { useEffect, useState } from 'react'
import { CloseIcon, PlusIcon } from './Icons'
import { colors } from '../data/products'

export const priceRanges = [
  { id: 'u50', label: 'Under $50', test: (p) => p < 50 },
  { id: '50-100', label: '$50 – $100', test: (p) => p >= 50 && p <= 100 },
  { id: 'o100', label: 'Over $100', test: (p) => p > 100 },
]

export const emptyFilters = { colors: [], prices: [] }

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
          <h2 className="display text-xl">Filter</h2>
          <button aria-label="Close filters" onClick={onClose}><CloseIcon /></button>
        </div>

        <div className="flex-1 overflow-y-auto px-6">
          <Section title="Colour">
            <div className="flex flex-wrap gap-2">
              {colors.map((c) => {
                const on = filters.colors.includes(c.name)
                return (
                  <button
                    key={c.name}
                    onClick={() => onChange({ ...filters, colors: toggle(filters.colors, c.name) })}
                    className={`flex items-center gap-2 rounded-full border py-1.5 pl-1.5 pr-3.5 text-[13px] transition-colors ${
                      on ? 'border-ink bg-ink text-paper' : 'border-line hover:border-ink'
                    }`}
                  >
                    <span className="h-5 w-5 rounded-full ring-1 ring-ink/15" style={{ background: c.hex }} />
                    {c.name}
                  </button>
                )
              })}
            </div>
          </Section>

          <Section title="Price">
            <div className="flex flex-wrap gap-2">
              {priceRanges.map((r) => {
                const on = filters.prices.includes(r.id)
                return (
                  <button
                    key={r.id}
                    onClick={() => onChange({ ...filters, prices: toggle(filters.prices, r.id) })}
                    className={`rounded-full border px-4 py-2 text-[13px] transition-colors ${
                      on ? 'border-ink bg-ink text-paper' : 'border-line hover:border-ink'
                    }`}
                  >
                    {r.label}
                  </button>
                )
              })}
            </div>
          </Section>
        </div>

        <div className="grid grid-cols-2 gap-3 border-t border-line p-6">
          <button onClick={() => onChange(emptyFilters)} className="btn-outline">Clear all</button>
          <button onClick={onClose} className="btn-solid">Show {resultCount} items</button>
        </div>
      </aside>
    </div>
  )
}
