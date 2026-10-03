import { categories } from '../data/products'

export const sortOptions = [
  { value: 'featured', label: 'Featured' },
  { value: 'new', label: 'Newest' },
  { value: 'price-asc', label: 'Price: Low to High' },
  { value: 'price-desc', label: 'Price: High to Low' },
]

export default function Toolbar({ category, onCategory, sort, onSort, cols, onCols, onOpenFilters, activeFilterCount, resultCount }) {
  return (
    <div className="sticky top-16 z-30 border-y border-line bg-paper/95 backdrop-blur">
      <div className="container-x flex h-14 items-center gap-6">
        {/* Category tabs */}
        <div className="-mx-1 flex flex-1 gap-1 overflow-x-auto [scrollbar-width:none]">
          {categories.map((c) => (
            <button
              key={c}
              onClick={() => onCategory(c)}
              className={`whitespace-nowrap rounded-full px-3.5 py-1.5 text-[13px] transition-colors duration-300 ${
                category === c ? 'bg-ink text-paper' : 'text-ink-2 hover:bg-paper-2'
              }`}
            >
              {c}
            </button>
          ))}
        </div>

        <span className="eyebrow hidden text-muted md:block">{resultCount} items</span>

        {/* Grid density */}
        <div className="hidden items-center gap-2 lg:flex" aria-label="Grid density">
          {[2, 3, 4].map((n) => (
            <button
              key={n}
              onClick={() => onCols(n)}
              aria-label={`${n} columns`}
              className={`flex h-6 items-center gap-[2px] px-1 transition-opacity ${cols === n ? 'opacity-100' : 'opacity-30 hover:opacity-60'}`}
            >
              {Array.from({ length: n }).map((_, i) => (
                <span key={i} className="h-3.5 w-[5px] bg-ink" />
              ))}
            </button>
          ))}
        </div>

        <label className="hidden items-center gap-2 sm:flex">
          <span className="eyebrow text-muted">Sort</span>
          <select
            value={sort}
            onChange={(e) => onSort(e.target.value)}
            className="cursor-pointer bg-transparent text-[13px] focus:outline-none"
          >
            {sortOptions.map((o) => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>
        </label>

        <button onClick={onOpenFilters} className="btn-outline px-4 py-2">
          Filter
          {activeFilterCount > 0 && (
            <span className="flex h-4 min-w-4 items-center justify-center rounded-full bg-accent px-1 text-[10px] text-on-accent">
              {activeFilterCount}
            </span>
          )}
        </button>
      </div>
    </div>
  )
}
