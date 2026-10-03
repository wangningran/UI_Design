import { AmpIcon, AmpStacked, Ball, BallWordmark, Crest, DivotIcon, DivotLockup, FlagD, FlagLockup } from './Marks'

const concepts = [
  {
    no: '01',
    name: 'Ball O',
    header: <BallWordmark className="text-[17px]" />,
    idea: 'The O in DIVOT becomes a coral golf ball. Instantly reads "golf", clean and confident.',
    mood: 'Sporty · Modern',
    primary: <BallWordmark className="text-[clamp(2.2rem,5vw,3.6rem)]" />,
    icon: (s) => (
      <span style={{ fontSize: s }} className="inline-flex">
        <Ball />
      </span>
    ),
  },
  {
    no: '02',
    name: 'Flying Divot',
    header: <DivotLockup className="text-[15px]" />,
    idea: 'A ball and the chunk of turf it just took — the moment of a pure iron strike.',
    mood: 'Story · Insider',
    primary: <DivotLockup className="text-[clamp(1.8rem,4vw,2.9rem)]" />,
    icon: (s) => <DivotIcon size={s} />,
  },
  {
    no: '03',
    name: 'Club Crest',
    header: <Crest size={44} />,
    idea: 'A round clubhouse badge. Leans into the heritage of "& Co"; great for embroidery on caps and towels.',
    mood: 'Heritage · Premium',
    primary: <Crest size={170} />,
    icon: (s) => <Crest size={s} />,
  },
  {
    no: '04',
    name: 'Big Ampersand',
    header: <AmpStacked className="text-[15px]" />,
    idea: 'The coral & is the hero. Stacked lockup for packaging, the & alone as the app-style icon.',
    mood: 'Bold · Graphic',
    primary: <AmpStacked className="text-[clamp(2.6rem,6vw,4.2rem)]" />,
    icon: (s) => <AmpIcon size={s} />,
  },
  {
    no: '05',
    name: 'Flag D',
    header: <FlagLockup className="text-[16px]" />,
    idea: 'The D is drawn as a flagstick with a coral pennant — the pin you play towards.',
    mood: 'Clever · Iconic',
    primary: <FlagLockup className="text-[clamp(2rem,4.6vw,3.2rem)]" />,
    icon: (s) => <FlagD size={s} />,
  },
]

function Tile({ dark = false, children, label }) {
  return (
    <div className={`relative flex min-h-56 items-center justify-center rounded-xl p-8 ${dark ? 'bg-night text-paper' : 'bg-paper-2 text-ink'}`}>
      {children}
      <span className={`eyebrow absolute bottom-3 left-4 ${dark ? 'text-paper/50' : 'text-muted'}`}>{label}</span>
    </div>
  )
}

export default function LogoConcepts() {
  return (
    <main className="container-x py-12 lg:py-20">
      <header className="grid gap-6 border-b border-line pb-10 lg:grid-cols-12 lg:items-end">
        <div className="lg:col-span-8">
          <p className="eyebrow text-muted">Divot &amp; Co · Brand identity · Round 1</p>
          <h1 className="display mt-5 text-[clamp(2.4rem,7vw,6rem)]">Logo concepts</h1>
        </div>
        <p className="max-w-md text-[15px] leading-relaxed text-ink-2 lg:col-span-4 lg:justify-self-end">
          Five directions in the Sunset Coral palette. Each is shown on light and forest grounds, at
          icon sizes, and in the site header. Pick one — or mix parts — and we refine from there.
        </p>
      </header>

      <div className="divide-y divide-line">
        {concepts.map((c) => (
          <section key={c.no} className="grid gap-8 py-14 lg:grid-cols-12">
            <div className="lg:col-span-3">
              <p className="display text-5xl text-accent">{c.no}</p>
              <h2 className="display mt-4 text-2xl">{c.name}</h2>
              <p className="eyebrow mt-3 text-muted">{c.mood}</p>
              <p className="mt-4 max-w-xs text-[14px] leading-relaxed text-ink-2">{c.idea}</p>
            </div>

            <div className="grid gap-4 sm:grid-cols-2 lg:col-span-9">
              <Tile label="Primary · light">{c.primary}</Tile>
              <Tile dark label="Primary · forest">{c.primary}</Tile>

              <Tile label="Icon · 96 / 48 / 32 / 16 px">
                <div className="flex items-end gap-6">
                  {[96, 48, 32, 16].map((s) => (
                    <span key={s} className="inline-flex">{c.icon(s)}</span>
                  ))}
                </div>
              </Tile>

              <Tile label="In the header">
                <div className="w-full overflow-hidden rounded-lg border border-line bg-paper">
                  <div className="flex h-14 items-center justify-between px-4 text-[12px] text-ink-2">
                    <span>Shop</span>
                    <span className="text-ink">{c.header}</span>
                    <span>Bag (0)</span>
                  </div>
                </div>
              </Tile>
            </div>
          </section>
        ))}
      </div>

      <footer className="border-t border-line pt-8">
        <a href="/" className="btn-outline">← Back to the shop</a>
      </footer>
    </main>
  )
}
