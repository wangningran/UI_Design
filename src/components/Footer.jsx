const columns = [
  ['Shop', ['New In', 'Headcovers', 'Headwear', 'Bags', 'On-Course']],
  ['Help', ['Shipping', 'Returns', 'Care Guide', 'Contact']],
  ['About', ['Our Story', 'Materials', 'Journal', 'Stores']],
  ['Follow', ['Instagram', 'TikTok', 'YouTube']],
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
          <p className="eyebrow text-muted">Studio Golf</p>
          <p className="mt-4">Golf accessories with tour-grade build and a lot more colour. Shipping worldwide.</p>
        </div>
      </div>

      {/* Oversized wordmark sign-off */}
      <div className="container-x mt-20 overflow-hidden">
        <p className="display flex select-none items-end gap-[0.04em] text-[clamp(4rem,17vw,17rem)] leading-[0.8]">
          Studio
          <span className="mb-[0.08em] inline-block h-[0.32em] w-[0.32em] shrink-0 rounded-full bg-accent" />
        </p>
      </div>
      <div className="container-x flex flex-wrap justify-between gap-4 border-t border-line py-6">
        <p className="eyebrow text-muted">© {new Date().getFullYear()} Studio Golf</p>
        <p className="eyebrow text-muted">Privacy · Terms · Accessibility</p>
      </div>
    </footer>
  )
}
