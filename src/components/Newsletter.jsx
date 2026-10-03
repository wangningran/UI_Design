import { useState } from 'react'
import { ArrowIcon } from './Icons'

export default function Newsletter() {
  const [done, setDone] = useState(false)
  return (
    <section className="bg-night text-paper">
      <div className="container-x grid gap-10 py-20 lg:grid-cols-12 lg:py-28">
        <h2 className="font-serif text-[clamp(2.25rem,5vw,4.5rem)] font-light leading-[1] tracking-tight lg:col-span-7">
          Letters from the road, <em className="text-paper/60">once a month.</em>
        </h2>
        <form
          className="self-end lg:col-span-5"
          onSubmit={(e) => {
            e.preventDefault()
            setDone(true)
          }}
        >
          <label className="eyebrow text-paper/60" htmlFor="email">Email address</label>
          <div className="mt-3 flex items-center border-b border-paper/40 focus-within:border-paper">
            <input
              id="email"
              type="email"
              required
              placeholder="you@example.com"
              className="flex-1 bg-transparent py-3 text-[16px] placeholder:text-paper/30 focus:outline-none"
            />
            <button aria-label="Subscribe" className="p-2 transition-transform hover:translate-x-1">
              <ArrowIcon />
            </button>
          </div>
          <p className="mt-3 text-[13px] text-paper/50">
            {done ? 'Thank you — you’re on the list.' : 'New releases, stories and early access. No noise.'}
          </p>
        </form>
      </div>
    </section>
  )
}
