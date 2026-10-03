// Divot & Co — logo concepts. Every mark uses currentColor for the ink parts
// and the accent token for coral, so each works on light and dark grounds.

const ACCENT = 'var(--accent)'

/* ---------- 01 · Ball O — wordmark, the O of DIVOT is a golf ball ---------- */

export function Ball({ className = '', fill = ACCENT }) {
  return (
    <span
      className={`inline-block shrink-0 rounded-full ${className}`}
      style={{
        width: '0.74em',
        height: '0.74em',
        backgroundColor: fill,
        // highlight + dimple texture
        backgroundImage:
          'radial-gradient(circle at 34% 30%, rgb(255 255 255 / 0.4) 0 16%, transparent 17%), radial-gradient(circle, rgb(0 0 0 / 0.13) 0.04em, transparent 0.045em)',
        backgroundSize: '100% 100%, 0.15em 0.15em',
      }}
    />
  )
}

export function BallWordmark({ className = '' }) {
  return (
    <span className={`display inline-flex items-center whitespace-nowrap leading-none ${className}`}>
      DIV<Ball className="mx-[0.02em]" />T<span className="ml-[0.28em] text-accent">&amp;</span><span className="ml-[0.2em]">CO</span>
    </span>
  )
}

/* ---------- 02 · Flying Divot — ball + turf chunk in flight ---------- */

export function DivotIcon({ size = 48, className = '' }) {
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" className={className} aria-hidden="true">
      <circle cx="44" cy="18" r="10" fill={ACCENT} />
      {/* turf chunk with grass blades on top */}
      <path d="M6 48c11-9 31-11 52-4-15-1-29 3-41 11-6 1-10-2-11-7Z" fill="currentColor" />
      <path d="M15 42l-3-7M22 39.5l-1-8M29 38.5l1.5-7" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" />
    </svg>
  )
}

export function DivotLockup({ className = '' }) {
  return (
    <span className={`inline-flex items-center gap-[0.35em] ${className}`}>
      <DivotIcon size="1.6em" />
      <span className="display whitespace-nowrap leading-none">
        Divot <span className="text-accent">&amp;</span> Co
      </span>
    </span>
  )
}

/* ---------- 03 · Club Crest — round badge for the heritage "& Co" ---------- */

export function Crest({ size = 160, className = '' }) {
  return (
    <svg width={size} height={size} viewBox="0 0 200 200" className={className} aria-label="Divot & Co crest">
      <defs>
        <path id="crest-top" d="M28 100a72 72 0 0 1 144 0" />
        <path id="crest-bottom" d="M18 100a82 82 0 0 0 164 0" />
      </defs>
      <circle cx="100" cy="100" r="96" fill="none" stroke="currentColor" strokeWidth="3" />
      <circle cx="100" cy="100" r="62" fill="none" stroke="currentColor" strokeWidth="1.5" />
      <text className="display" fontSize="20" fill="currentColor" letterSpacing="3">
        <textPath href="#crest-top" startOffset="50%" textAnchor="middle">DIVOT &amp; CO</textPath>
      </text>
      <text fontFamily="var(--font-mono)" fontSize="10.5" fill="currentColor" letterSpacing="2.5">
        <textPath href="#crest-bottom" startOffset="50%" textAnchor="middle">GOLF ACCESSORIES · EST. 2026</textPath>
      </text>
      <circle cx="22" cy="100" r="3.5" fill={ACCENT} />
      <circle cx="178" cy="100" r="3.5" fill={ACCENT} />
      <circle cx="100" cy="100" r="44" fill={ACCENT} />
      <text x="100" y="117" textAnchor="middle" className="display" fontSize="50" fill="var(--on-accent)">&amp;</text>
    </svg>
  )
}

/* ---------- 04 · Big Ampersand — the & as the hero icon ---------- */

export function AmpIcon({ size = 48, className = '' }) {
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" className={className} aria-hidden="true">
      <rect width="64" height="64" rx="16" fill={ACCENT} />
      <text x="32" y="47" textAnchor="middle" className="display" fontSize="42" fill="var(--on-accent)">&amp;</text>
    </svg>
  )
}

export function AmpStacked({ className = '' }) {
  return (
    <span className={`display relative inline-grid leading-[0.82] ${className}`}>
      <span>Divot</span>
      <span className="flex items-baseline gap-[0.12em]">
        <span className="text-accent text-[1.35em] leading-[0.6]">&amp;</span>
        <span>Co</span>
      </span>
    </span>
  )
}

/* ---------- 05 · Flag D — the D is a flagstick and pennant ---------- */

export function FlagD({ size = 48, className = '' }) {
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" className={className} aria-hidden="true">
      {/* flagstick = stem of the D, pennant = its bowl */}
      <rect x="12" y="8" width="7" height="46" rx="1.5" fill="currentColor" />
      <path d="M19 8h9a23 23 0 0 1 0 46h-9Z" fill={ACCENT} />
      <ellipse cx="16" cy="58.5" rx="12" ry="2.4" fill="currentColor" opacity="0.25" />
    </svg>
  )
}

export function FlagLockup({ className = '' }) {
  return (
    <span className={`inline-flex items-center gap-[0.2em] ${className}`}>
      <FlagD size="1.5em" />
      <span className="display whitespace-nowrap leading-none">
        ivot <span className="text-accent">&amp;</span> Co
      </span>
    </span>
  )
}
