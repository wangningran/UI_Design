import { useEffect, useState } from 'react'
import Logo from './Logo'
import { BagIcon, CloseIcon, MenuIcon, SearchIcon, UserIcon } from './Icons'

const nav = ['Shop', 'New In', 'Headcovers', 'Journal', 'Clubhouse']

export default function Header({ cartCount }) {
  const [scrolled, setScrolled] = useState(false)
  const [open, setOpen] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8)
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <>
      <div className="bg-night text-paper">
        <p className="container-x eyebrow py-2 text-center text-paper/80">
          Free shipping over $100 · <span className="text-accent">New season headcovers just dropped</span>
        </p>
      </div>

      <header
        className={`sticky top-0 z-40 border-b transition-colors duration-500 ${
          scrolled ? 'border-line bg-paper/90 backdrop-blur' : 'border-transparent bg-paper'
        }`}
      >
        <div className="container-x grid h-16 grid-cols-[1fr_auto_1fr] items-center">
          <nav className="hidden items-center gap-7 lg:flex">
            {nav.map((item) => (
              <a key={item} href="#" className={`link-underline text-[13px] ${item === 'Shop' ? 'text-ink' : 'text-ink-2'}`}>
                {item}
              </a>
            ))}
          </nav>
          <button className="lg:hidden" aria-label="Open menu" onClick={() => setOpen(true)}>
            <MenuIcon />
          </button>

          <a href="#" aria-label="Studio Golf home">
            <Logo className="text-lg" />
          </a>

          <div className="flex items-center justify-end gap-5">
            <button aria-label="Search" className="hover:text-accent transition-colors"><SearchIcon /></button>
            <button aria-label="Account" className="hidden sm:block hover:text-accent transition-colors"><UserIcon /></button>
            <button aria-label="Bag" className="relative flex items-center gap-1.5 hover:text-accent transition-colors">
              <BagIcon />
              <span
                key={cartCount}
                className={`flex h-5 min-w-5 items-center justify-center rounded-full px-1 font-mono text-[10px] tabular-nums ${
                  cartCount ? 'animate-[pop_0.4s_var(--ease-soft)] bg-accent text-on-accent' : 'bg-paper-2'
                }`}
              >
                {cartCount}
              </span>
            </button>
          </div>
        </div>
      </header>

      {/* Mobile menu */}
      <div className={`fixed inset-0 z-50 lg:hidden ${open ? '' : 'pointer-events-none'}`}>
        <div
          className={`absolute inset-0 bg-ink/30 transition-opacity duration-500 ${open ? 'opacity-100' : 'opacity-0'}`}
          onClick={() => setOpen(false)}
        />
        <div
          className={`absolute inset-y-0 left-0 w-[85%] max-w-sm bg-paper p-6 transition-transform duration-500 ease-soft ${
            open ? 'translate-x-0' : '-translate-x-full'
          }`}
        >
          <button aria-label="Close menu" onClick={() => setOpen(false)}><CloseIcon /></button>
          <ul className="mt-10 space-y-5">
            {nav.map((item) => (
              <li key={item}><a href="#" className="display text-3xl">{item}</a></li>
            ))}
          </ul>
        </div>
      </div>
    </>
  )
}
