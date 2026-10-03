import ImageSlot from './ImageSlot'

const stats = [
  ['600D', 'Recycled tour nylon'],
  ['3x', 'Double-stitched seams'],
  ['100%', 'Magnetic closures'],
]

// Split section: image on one side, material story and proof points on the other.
export default function StorySplit() {
  return (
    <section className="container-x pb-20 lg:pb-28">
      <div className="grid overflow-hidden rounded-2xl bg-paper-2 lg:grid-cols-2">
        <ImageSlot ratio="1 / 1" label="Craft image" />
        <div className="flex flex-col justify-center gap-8 px-6 py-14 lg:px-16">
          <p className="eyebrow text-muted">Built for the tour, made for you</p>
          <h2 className="display max-w-lg text-[clamp(2rem,3.6vw,3.4rem)]">Engineered down to the stitch.</h2>
          <p className="max-w-md text-[15px] leading-relaxed text-ink-2">
            Every headcover starts with recycled tour nylon and a fleece lining that protects your clubs from
            the trunk to the 18th. Magnetic closures, reinforced seams, colours that stay bright season after season.
          </p>
          <dl className="grid max-w-md grid-cols-3 gap-4 border-t border-line pt-6">
            {stats.map(([n, l]) => (
              <div key={n}>
                <dt className="display text-2xl">{n}</dt>
                <dd className="mt-1.5 text-[12px] leading-snug text-muted">{l}</dd>
              </div>
            ))}
          </dl>
          <a href="#" className="btn-solid self-start">Discover the craft</a>
        </div>
      </div>
    </section>
  )
}
