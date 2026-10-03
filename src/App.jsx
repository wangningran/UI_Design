import { Fragment, useCallback, useMemo, useState } from 'react'
import Header from './components/Header'
import CollectionHero from './components/CollectionHero'
import Toolbar from './components/Toolbar'
import ProductCard from './components/ProductCard'
import EditorialTile from './components/EditorialTile'
import FilterDrawer, { emptyFilters, priceRanges } from './components/FilterDrawer'
import Marquee from './components/Marquee'
import StorySplit from './components/StorySplit'
import Newsletter from './components/Newsletter'
import Footer from './components/Footer'
import { products } from './data/products'

const PAGE_SIZE = 14 // 14 products + 1 editorial tile (2 slots) = 4 full rows at 4 columns
const gridCols = { 2: 'lg:grid-cols-2', 3: 'lg:grid-cols-3', 4: 'lg:grid-cols-4' }

export default function App() {
  const [category, setCategory] = useState('All')
  const [sort, setSort] = useState('featured')
  const [cols, setCols] = useState(4)
  const [filters, setFilters] = useState(emptyFilters)
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [visible, setVisible] = useState(PAGE_SIZE)
  const [cart, setCart] = useState([])
  const [toast, setToast] = useState(null)

  const results = useMemo(() => {
    const list = products.filter((p) => {
      if (category !== 'All' && p.category !== category) return false
      if (filters.colors.length && !p.colors.some((c) => filters.colors.includes(c))) return false
      if (filters.prices.length && !priceRanges.some((r) => filters.prices.includes(r.id) && r.test(p.price))) return false
      return true
    })
    const sorters = {
      featured: (a, b) => a.order - b.order,
      new: (a, b) => (b.badge === 'New') - (a.badge === 'New') || a.order - b.order,
      'price-asc': (a, b) => a.price - b.price,
      'price-desc': (a, b) => b.price - a.price,
    }
    return [...list].sort(sorters[sort])
  }, [category, filters, sort])

  const activeFilterCount = filters.colors.length + filters.prices.length
  const shown = results.slice(0, visible)
  // Place the story tile so it completes the second row at the chosen density.
  const editorialAt = cols === 2 ? 4 : cols * 2 - 2

  const addToCart = (product, colour) => {
    setCart((c) => [...c, { id: product.id, colour }])
    setToast(`${product.name} — ${colour}`)
    setTimeout(() => setToast(null), 2200)
  }

  const resetPaging = (fn) => (v) => {
    fn(v)
    setVisible(PAGE_SIZE)
  }

  const closeDrawer = useCallback(() => setDrawerOpen(false), [])

  return (
    <>
      <Header cartCount={cart.length} />

      <main>
        <CollectionHero count={products.length} />
        <Marquee />

        <Toolbar
          category={category}
          onCategory={resetPaging(setCategory)}
          sort={sort}
          onSort={setSort}
          cols={cols}
          onCols={setCols}
          onOpenFilters={() => setDrawerOpen(true)}
          activeFilterCount={activeFilterCount}
          resultCount={results.length}
        />

        <section className="container-x py-10 lg:py-14">
          {results.length === 0 ? (
            <div className="py-32 text-center">
              <p className="display text-3xl">Nothing matches — yet.</p>
              <button onClick={() => setFilters(emptyFilters)} className="btn-outline mt-6">
                Clear filters
              </button>
            </div>
          ) : (
            <div className={`grid grid-cols-2 gap-x-3 gap-y-12 sm:gap-x-5 lg:gap-y-16 ${gridCols[cols]}`}>
              {shown.map((p, i) => (
                <Fragment key={p.id}>
                  {i === editorialAt && <EditorialTile className="col-span-2" />}
                  <ProductCard product={p} onAdd={addToCart} />
                </Fragment>
              ))}
            </div>
          )}

          {results.length > 0 && (
            <div className="mx-auto mt-20 flex max-w-xs flex-col items-center gap-4">
              <p className="eyebrow text-muted">
                Showing {shown.length} of {results.length}
              </p>
              <div className="h-px w-full bg-line">
                <div className="h-px bg-ink transition-all duration-700 ease-soft" style={{ width: `${(shown.length / results.length) * 100}%` }} />
              </div>
              {shown.length < results.length && (
                <button onClick={() => setVisible((v) => v + PAGE_SIZE)} className="btn-outline mt-2 px-8">
                  Load more
                </button>
              )}
            </div>
          )}
        </section>

        <StorySplit />
        <Newsletter />
      </main>

      <Footer />

      <FilterDrawer
        open={drawerOpen}
        onClose={closeDrawer}
        filters={filters}
        onChange={resetPaging(setFilters)}
        resultCount={results.length}
      />

      {/* Add-to-bag toast */}
      <div
        role="status"
        className={`fixed bottom-6 left-1/2 z-50 flex -translate-x-1/2 items-center gap-2.5 rounded-full bg-ink px-5 py-3 text-paper transition-all duration-500 ease-soft ${
          toast ? 'translate-y-0 opacity-100' : 'pointer-events-none translate-y-4 opacity-0'
        }`}
      >
        <span className="h-2 w-2 rounded-full bg-accent" />
        <p className="eyebrow whitespace-nowrap">Added to bag · {toast}</p>
      </div>
    </>
  )
}
