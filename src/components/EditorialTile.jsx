import ImageSlot from './ImageSlot'
import { ArrowIcon } from './Icons'

// A story tile that interrupts the product grid.
export default function EditorialTile({ className = '' }) {
  return (
    <a href="#" className={`group relative block overflow-hidden rounded-xl bg-night text-paper ${className}`}>
      <div className="grid h-full md:grid-cols-2">
        <ImageSlot ratio="4 / 5" label="Lifestyle image" className="opacity-80 max-md:aspect-[16/10]! md:h-full" />
        <div className="flex flex-col justify-between gap-10 p-6 lg:p-10">
          <span className="eyebrow self-start rounded-full bg-accent px-2.5 py-1 text-on-accent">The Journal</span>
          <div>
            <h3 className="display text-[clamp(1.6rem,2.6vw,2.6rem)]">
              The weekend round, reimagined.
            </h3>
            <p className="mt-4 max-w-sm text-[14px] leading-relaxed text-paper/70">
              Early tee times, loud headcovers and the kit that keeps a four-ball moving.
            </p>
          </div>
          <span className="eyebrow inline-flex items-center gap-2">
            Read the story
            <ArrowIcon className="transition-transform duration-500 ease-soft group-hover:translate-x-1.5" />
          </span>
        </div>
      </div>
    </a>
  )
}
