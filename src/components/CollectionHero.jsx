export default function CollectionHero({ count }) {
  return (
    <section className="container-x pt-10 pb-12 lg:pt-16 lg:pb-16">
      <p className="eyebrow text-muted">
        <a href="#" className="link-underline">Home</a> <span className="mx-1.5">/</span> Shop All
      </p>
      <div className="mt-8 grid gap-8 lg:grid-cols-12 lg:items-end">
        <h1 className="display text-[clamp(2.4rem,7vw,6.5rem)] lg:col-span-8">
          Golf
          <br />
          Accessories
          <sup className="eyebrow ml-3 align-top font-normal tracking-[0.14em] text-muted">({count})</sup>
        </h1>
        <div className="lg:col-span-4 lg:justify-self-end">
          <p className="max-w-md text-[15px] leading-relaxed text-ink-2">
            Headcovers, bags and on-course essentials — engineered with tour-grade materials and finished
            in colours made for the first tee.
          </p>
          <div className="mt-6 flex flex-wrap gap-2">
            {['Tour-grade', 'Lifetime stitching', 'Free returns'].map((t) => (
              <span key={t} className="eyebrow rounded-full border border-line px-3 py-1.5 text-ink-2">{t}</span>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
