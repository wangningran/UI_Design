import ImageSlot from './ImageSlot'
import { ArrowIcon } from './Icons'

// A story tile that interrupts the product grid (Tracksmith / Aesop pattern).
export default function EditorialTile({ className = '' }) {
  return (
    <a href="#" className={`group relative block overflow-hidden bg-night text-paper ${className}`}>
      <div className="grid h-full md:grid-cols-2">
        <ImageSlot ratio="4 / 5" label="Editorial image" className="opacity-80 md:h-full" />
        <div className="flex flex-col justify-between gap-10 p-6 lg:p-10">
          <p className="eyebrow text-paper/60">Journal — No. 07</p>
          <div>
            <h3 className="font-serif text-[clamp(1.75rem,3vw,2.75rem)] font-light leading-[1.05] tracking-tight">
              The quiet hours: notes on running before dawn.
            </h3>
            <p className="mt-4 max-w-sm text-[14px] leading-relaxed text-paper/70">
              A field guide to early miles, cold air and the gear that makes them easier.
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
