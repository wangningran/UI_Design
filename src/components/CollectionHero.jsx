export default function CollectionHero({ count }) {
  return (
    <section className="container-x pt-10 pb-12 lg:pt-16 lg:pb-20">
      <p className="eyebrow text-muted">
        <a href="#" className="link-underline">Home</a> <span className="mx-1.5">/</span> Shop All
      </p>
      <div className="mt-8 grid gap-8 lg:grid-cols-12 lg:items-end">
        <h1 className="font-serif text-[clamp(3rem,9vw,8.5rem)] font-light leading-[0.9] tracking-[-0.03em] lg:col-span-8">
          Shop All
          <sup className="eyebrow ml-3 align-top text-muted">({count})</sup>
        </h1>
        <p className="max-w-md text-[15px] leading-relaxed text-ink-2 lg:col-span-4 lg:justify-self-end">
          Considered essentials for the daily practice. Built from honest materials, cut for movement,
          and made to outlast the season.
        </p>
      </div>
    </section>
  )
}
