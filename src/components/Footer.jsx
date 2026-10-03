const columns = [
  ['Shop', ['New Arrivals', 'Tops', 'Bottoms', 'Outerwear', 'Accessories']],
  ['Help', ['Shipping', 'Returns', 'Size Guide', 'Contact']],
  ['About', ['Our Story', 'Materials', 'Journal', 'Stores']],
  ['Follow', ['Instagram', 'Strava', 'YouTube']],
]

export default function Footer() {
  return (
    <footer className="bg-paper pt-16">
      <div className="container-x grid grid-cols-2 gap-10 md:grid-cols-4 lg:grid-cols-6">
        {columns.map(([title, links]) => (
          <div key={title}>
            <p className="eyebrow text-muted">{title}</p>
            <ul className="mt-4 space-y-2.5">
              {links.map((l) => (
                <li key={l}><a href="#" className="link-underline text-[14px]">{l}</a></li>
              ))}
            </ul>
          </div>
        ))}
        <div className="col-span-2 text-[14px] leading-relaxed text-ink-2">
          <p className="eyebrow text-muted">Studio</p>
          <p className="mt-4">Designed for the daily practice. Shipping worldwide from our studio.</p>
        </div>
      </div>

      {/* Oversized wordmark — Satisfy-style typographic sign-off */}
      <div className="container-x mt-20 overflow-hidden">
        <p className="select-none font-serif text-[clamp(5rem,24vw,22rem)] font-light leading-[0.78] tracking-[-0.05em]">
          Studio<span className="text-accent">.</span>
        </p>
      </div>
      <div className="container-x flex flex-wrap justify-between gap-4 border-t border-line py-6">
        <p className="eyebrow text-muted">© {new Date().getFullYear()} Studio</p>
        <p className="eyebrow text-muted">Privacy · Terms · Accessibility</p>
      </div>
    </footer>
  )
}
