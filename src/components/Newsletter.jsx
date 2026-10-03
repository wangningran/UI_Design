import { useState } from 'react'
import { ArrowIcon } from './Icons'

export default function Newsletter() {
  const [done, setDone] = useState(false)
  return (
    <section className="bg-night text-paper">
      <div className="container-x grid gap-10 py-20 lg:grid-cols-12 lg:py-28">
        <h2 className="display text-[clamp(2.2rem,5vw,4.6rem)] lg:col-span-7">
          Join the <span className="text-accent">clubhouse.</span>
        </h2>
        <form
          className="self-end lg:col-span-5"
          onSubmit={(e) => {
            e.preventDefault()
            setDone(true)
          }}
        >
          <label className="eyebrow text-paper/60" htmlFor="email">Early drops, member pricing, tee-time stories</label>
          <div className="mt-4 flex items-center rounded-full bg-paper/10 p-1.5 pl-5 ring-1 ring-paper/20 focus-within:ring-accent">
            <input
              id="email"
              type="email"
              required
              placeholder="you@example.com"
              className="flex-1 bg-transparent py-2 text-[15px] placeholder:text-paper/40 focus:outline-none"
            />
            <button aria-label="Subscribe" className="flex h-10 w-10 items-center justify-center rounded-full bg-accent text-on-accent transition-transform hover:scale-105">
              <ArrowIcon />
            </button>
          </div>
          <p className="mt-3 text-[13px] text-paper/50">
            {done ? 'Welcome to the clubhouse — check your inbox.' : 'One email a month. No spam, ever.'}
          </p>
        </form>
      </div>
    </section>
  )
}
