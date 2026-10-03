// Scrolling accent band — the sporty, kinetic counterpoint to the calm grid.
const items = ['Tour-grade materials', 'Designed for the weekend round', 'Free shipping over $100', 'Made to be seen on the first tee']

export default function Marquee() {
  const row = [...items, ...items]
  return (
    <div className="overflow-hidden bg-accent py-3 text-on-accent">
      <div className="animate-marquee flex w-max">
        {[0, 1].map((k) => (
          <div key={k} className="flex shrink-0" aria-hidden={k === 1}>
            {row.map((t, i) => (
              <span key={i} className="display flex items-center whitespace-nowrap px-6 text-[13px] tracking-[0.02em]">
                {t}
                <span className="ml-12 inline-block h-1.5 w-1.5 rounded-full bg-on-accent" />
              </span>
            ))}
          </div>
        ))}
      </div>
    </div>
  )
}
