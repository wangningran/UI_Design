import ImageSlot from './ImageSlot'

// Aesop-style split: image on one side, quiet editorial copy on the other.
export default function StorySplit() {
  return (
    <section className="border-t border-line">
      <div className="grid lg:grid-cols-2">
        <ImageSlot ratio="1 / 1" label="Brand image" />
        <div className="flex flex-col justify-center gap-8 px-6 py-16 lg:px-20">
          <p className="eyebrow text-muted">Our materials</p>
          <h2 className="max-w-lg font-serif text-[clamp(2rem,4vw,3.5rem)] font-light leading-[1.05] tracking-tight">
            Fewer things, made with more intent.
          </h2>
          <p className="max-w-md text-[15px] leading-relaxed text-ink-2">
            Every piece begins with fibre — merino from audited farms, recycled nylon spun in Italy,
            and seams engineered to disappear on the move. We design for the thousandth mile, not the first.
          </p>
          <a href="#" className="eyebrow link-underline self-start pb-1">Discover our process</a>
        </div>
      </div>
    </section>
  )
}
