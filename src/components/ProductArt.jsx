import { useId } from 'react'
import { colors } from '../data/products'

// Mock product illustrations (vector), drawn in the chosen colourway.
// Stand-ins until real photography exists — swap for <img> via product.images.

const CORAL = '#ff6b4a'
const INK = '#18201b'
const PAPER = '#faf7f2'
const FOREST = '#1f4d3a'
const LIGHT = ['White', 'Lime', 'Sky']

const hexOf = (name) => colors.find((c) => c.name === name)?.hex ?? name
const shade = (c, pct) => `color-mix(in srgb, ${c} ${100 - pct}%, #000)`
const tint = (c, pct) => `color-mix(in srgb, ${c} ${100 - pct}%, #fff)`

/* ---------- shared bits ---------- */

function BallMark({ x, y, r, fill = CORAL }) {
  return (
    <g>
      <circle cx={x} cy={y} r={r} style={{ fill }} />
      <circle cx={x - r * 0.32} cy={y - r * 0.34} r={r * 0.28} fill="#fff" opacity="0.4" />
    </g>
  )
}

function Word({ x, y, size = 16, fill, children }) {
  return (
    <text x={x} y={y} textAnchor="middle" className="display" fontSize={size} style={{ fill }} letterSpacing="0.5">
      {children}
    </text>
  )
}

const stitch = (detail) => ({ fill: 'none', stroke: detail, strokeWidth: 2, strokeDasharray: '6 5', opacity: 0.55 })

/* ---------- products ---------- */

function Headcover({ c, d, logo, uid, tag, small }) {
  const s = small ? 0.84 : 1
  const cy = small ? 195 : 178
  return (
    <g>
      <clipPath id={`${uid}-neck`}>
        <path d="M138 232 Q150 335 166 440 L234 440 Q250 335 262 232 Z" />
      </clipPath>
      <path d="M138 232 Q150 335 166 440 L234 440 Q250 335 262 232 Z" style={{ fill: shade(c, 8) }} />
      <g clipPath={`url(#${uid}-neck)`}>
        {[292, 322, 352].map((y) => (
          <rect key={y} x="100" y={y} width="200" height="13" style={{ fill: d }} opacity="0.85" />
        ))}
        <rect x="100" y="405" width="200" height="40" style={{ fill: shade(c, 18) }} />
        {Array.from({ length: 14 }).map((_, i) => (
          <line key={i} x1={150 + i * 7} y1="407" x2={150 + i * 7} y2="440" style={{ stroke: shade(c, 32) }} strokeWidth="2" />
        ))}
      </g>
      <ellipse cx="200" cy={cy} rx={110 * s} ry={92 * s} style={{ fill: c }} />
      <ellipse cx={200 - 38 * s} cy={cy - 40 * s} rx={42 * s} ry={22 * s} fill="#fff" opacity="0.18" />
      <ellipse cx="200" cy={cy} rx={98 * s} ry={80 * s} style={stitch(d)} />
      <BallMark x={200} y={cy - 6} r={20 * s} fill={logo} />
      <Word x={200} y={cy + 36 * s} size={15 * s} fill={d}>DIVOT &amp; CO</Word>
      <g transform={`translate(${200 + 82 * s} ${cy + 26 * s})`}>
        <rect x="-15" y="-15" width="30" height="30" rx="8" style={{ fill: d }} />
        <text textAnchor="middle" y="7" className="display" fontSize="18" style={{ fill: c }}>{tag}</text>
      </g>
    </g>
  )
}

function BladeCover({ c, d, logo }) {
  return (
    <g>
      <rect x="186" y="168" width="28" height="44" rx="6" style={{ fill: shade(c, 25) }} />
      <path d="M78 210 H322 V286 Q322 350 260 350 H140 Q78 350 78 286 Z" style={{ fill: c }} />
      <path d="M92 222 H308 V284 Q308 336 258 336 H142 Q92 336 92 284 Z" style={stitch(d)} />
      <path d="M78 210 H322 V232 H78 Z" style={{ fill: shade(c, 10) }} />
      <rect x="300" y="250" width="34" height="46" rx="8" style={{ fill: d }} opacity="0.9" />
      <BallMark x={150} y={284} r={20} fill={logo} />
      <Word x={225} y={292} size={22} fill={d}>DIVOT</Word>
    </g>
  )
}

function MalletCover({ c, d, logo }) {
  return (
    <g>
      <rect x="186" y="150" width="28" height="44" rx="6" style={{ fill: shade(c, 25) }} />
      <path d="M78 350 L322 350 Q330 190 200 186 Q70 190 78 350 Z" style={{ fill: c }} />
      <path d="M96 338 L304 338 Q310 204 200 200 Q90 204 96 338 Z" style={stitch(d)} />
      <ellipse cx="160" cy="232" rx="40" ry="18" fill="#fff" opacity="0.16" />
      <rect x="78" y="330" width="244" height="22" rx="6" style={{ fill: shade(c, 14) }} />
      <BallMark x={200} y={262} r={22} fill={logo} />
      <Word x={200} y={312} size={16} fill={d}>DIVOT &amp; CO</Word>
    </g>
  )
}

function Cap({ c, d, logo }) {
  return (
    <g>
      <path d="M118 296 Q60 302 34 334 Q110 342 196 312 Z" style={{ fill: shade(c, 14) }} />
      <path d="M110 300 Q108 166 228 156 Q336 160 334 296 Z" style={{ fill: c }} />
      <path d="M228 156 Q190 210 186 300 M228 156 Q270 210 284 298" style={{ fill: 'none', stroke: shade(c, 18) }} strokeWidth="2.5" />
      <ellipse cx="170" cy="200" rx="40" ry="20" fill="#fff" opacity="0.16" />
      <rect x="108" y="288" width="228" height="14" rx="4" style={{ fill: shade(c, 20) }} />
      <circle cx="228" cy="156" r="8" style={{ fill: shade(c, 22) }} />
      <rect x="128" y="226" width="78" height="44" rx="10" style={{ fill: d }} />
      <BallMark x={150} y={248} r={11} fill={logo} />
      <text x="184" y="254" textAnchor="middle" className="display" fontSize="13" style={{ fill: c }}>D&amp;C</text>
    </g>
  )
}

function BucketHat({ c, d, logo }) {
  return (
    <g>
      <ellipse cx="200" cy="300" rx="138" ry="40" style={{ fill: shade(c, 22) }} />
      <path d="M134 302 L150 182 Q200 166 250 182 L266 302 Z" style={{ fill: c }} />
      <ellipse cx="200" cy="182" rx="50" ry="12" style={{ fill: shade(c, 8) }} />
      <path d="M140 262 L260 262 L264 292 L136 292 Z" style={{ fill: d }} opacity="0.9" />
      <path d="M62 300 A138 40 0 0 0 338 300 L312 300 A112 28 0 0 1 88 300 Z" style={{ fill: c }} />
      <path d="M74 304 A126 34 0 0 0 326 304" style={stitch(d)} />
      <ellipse cx="174" cy="214" rx="20" ry="26" fill="#fff" opacity="0.15" />
      <BallMark x={200} y={226} r={16} fill={logo} />
    </g>
  )
}

function Visor({ c, d, logo }) {
  return (
    <g>
      <path d="M92 268 Q200 222 308 268 Q268 352 200 356 Q132 352 92 268 Z" style={{ fill: shade(c, 12) }} />
      <path d="M110 276 Q200 240 290 276" style={stitch(d)} />
      <path d="M96 232 Q200 186 304 232 L306 270 Q200 224 94 270 Z" style={{ fill: c }} />
      <rect x="166" y="210" width="68" height="30" rx="8" style={{ fill: d }} />
      <BallMark x={186} y={225} r={9} fill={logo} />
      <text x="214" y="231" textAnchor="middle" className="display" fontSize="12" style={{ fill: c }}>D&amp;C</text>
    </g>
  )
}

function StandBag({ c, d, logo, slim }) {
  const w = slim ? 76 : 104
  const x = 200 - w / 2
  return (
    <g>
      {!slim && (
        <>
          <line x1="246" y1="210" x2="300" y2="452" style={{ stroke: INK }} strokeWidth="6" strokeLinecap="round" />
          <line x1="240" y1="216" x2="270" y2="458" style={{ stroke: INK }} strokeWidth="6" strokeLinecap="round" />
        </>
      )}
      <g transform={`rotate(${slim ? -5 : -8} 200 300)`}>
        <ellipse cx="180" cy="86" rx="22" ry="18" fill={CORAL} />
        <ellipse cx="214" cy="80" rx="20" ry="17" style={{ fill: INK }} />
        <ellipse cx="236" cy="96" rx="16" ry="14" fill={PAPER} stroke={INK} strokeWidth="2" />
        <rect x={x} y="140" width={w} height="300" rx="34" style={{ fill: c }} />
        <rect x={x - 10} y="112" width={w + 20} height="44" rx="14" style={{ fill: shade(c, 16) }} />
        <rect x={x + 12} y="270" width={w - 24} height="120" rx="18" style={{ fill: shade(c, 8) }} />
        <line x1={x + 22} y1="292" x2={x + w - 22} y2="292" style={stitch(d)} />
        <rect x={x - 4} y="418" width={w + 8} height="26" rx="10" style={{ fill: shade(c, 22) }} />
        <BallMark x={200} y={196} r={16} fill={logo} />
        <Word x={200} y={240} size={slim ? 12 : 14} fill={d}>DIVOT</Word>
        <path
          d={`M${x + w - 4} 166 Q${x + w + 50} 250 ${x + w - 2} 360`}
          style={{ fill: 'none', stroke: d }}
          strokeWidth="9"
          strokeLinecap="round"
          opacity="0.9"
        />
      </g>
    </g>
  )
}

function Towel({ c, d, logo, uid }) {
  return (
    <g>
      <pattern id={`${uid}-waffle`} width="16" height="16" patternUnits="userSpaceOnUse">
        <path d="M0 0H16V16" style={{ fill: 'none', stroke: shade(c, 20) }} strokeWidth="2" />
      </pattern>
      <circle cx="200" cy="88" r="20" fill="none" stroke="#9aa1a6" strokeWidth="7" />
      <path d="M118 124 L282 124 L292 430 Q200 446 108 430 Z" style={{ fill: c }} />
      <path d="M118 124 L282 124 L292 430 Q200 446 108 430 Z" fill={`url(#${uid}-waffle)`} />
      <rect x="114" y="120" width="172" height="30" rx="4" style={{ fill: shade(c, 10) }} />
      <circle cx="200" cy="136" r="9" fill="#cfd3d6" stroke="#8d949a" strokeWidth="3" />
      <path d="M200 108 L200 127" stroke="#9aa1a6" strokeWidth="6" />
      <rect x="226" y="378" width="52" height="30" rx="5" fill={FOREST} />
      <BallMark x={242} y={393} r={8} fill={CORAL} />
      <text x="264" y="398" textAnchor="middle" className="display" fontSize="10" fill={PAPER}>D&amp;C</text>
      <path d="M150 160 Q160 300 148 420" stroke="#fff" strokeWidth="14" opacity="0.12" fill="none" />
    </g>
  )
}

function Ball({ x, y, r, c, uid }) {
  return (
    <g>
      <circle cx={x} cy={y} r={r} style={{ fill: c, stroke: shade(c, 14) }} strokeWidth="1.5" />
      <circle cx={x} cy={y} r={r} fill={`url(#${uid}-dimple)`} />
      <circle cx={x - r * 0.35} cy={y - r * 0.35} r={r * 0.3} fill="#fff" opacity="0.45" />
      <circle cx={x + r * 0.15} cy={y + r * 0.1} r={r * 0.17} fill={CORAL} />
    </g>
  )
}

function BallBox({ c, uid }) {
  return (
    <g>
      <pattern id={`${uid}-dimple`} width="9" height="9" patternUnits="userSpaceOnUse">
        <circle cx="4.5" cy="4.5" r="1.7" fill="#000" opacity="0.1" />
      </pattern>
      <path d="M96 168 L132 140 L332 140 L304 168 Z" fill={shade(FOREST, 25)} />
      <path d="M304 168 L332 140 L332 314 L304 342 Z" fill={shade(FOREST, 40)} />
      <rect x="96" y="168" width="208" height="174" fill={FOREST} />
      <Word x={200} y={226} size={30} fill={PAPER}>TOUR</Word>
      <BallMark x={162} y={262} r={12} fill={CORAL} />
      <text x="212" y="268" textAnchor="middle" className="display" fontSize="15" fill={PAPER}>DIVOT &amp; CO</text>
      <text x="200" y="300" textAnchor="middle" fontFamily="var(--font-mono)" fontSize="10" fill={PAPER} opacity="0.7" letterSpacing="2">12 BALLS · 3-PIECE</text>
      <Ball x={140} y={378} r={44} c={c} uid={uid} />
      <Ball x={262} y={382} r={44} c={c} uid={uid} />
      <Ball x={200} y={400} r={48} c={c} uid={uid} />
    </g>
  )
}

function Marker({ x, y, r, c, logo, uid }) {
  return (
    <g>
      <circle cx={x} cy={y + 5} r={r} fill="#000" opacity="0.12" />
      <circle cx={x} cy={y} r={r} fill={`url(#${uid}-metal)`} />
      <circle cx={x} cy={y} r={r * 0.76} style={{ fill: c }} />
      <circle cx={x} cy={y} r={r * 0.76} style={{ fill: 'none', stroke: shade(c, 20) }} strokeWidth="2" />
      <BallMark x={x} y={y} r={r * 0.3} fill={logo} />
    </g>
  )
}

function MarkerSet({ c, logo, uid, alt }) {
  return (
    <g>
      <linearGradient id={`${uid}-metal`} x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stopColor="#e9ecee" />
        <stop offset="1" stopColor="#8d949a" />
      </linearGradient>
      <rect x="226" y="150" width="64" height="120" rx="14" fill={`url(#${uid}-metal)`} />
      <rect x="240" y="166" width="36" height="70" rx="10" fill="#000" opacity="0.08" />
      <Marker x={258} y={236} r={46} c={alt} logo={logo} uid={uid} />
      <Marker x={146} y={292} r={56} c={c} logo={logo} uid={uid} />
      <Marker x={250} y={350} r={52} c={c} logo={logo} uid={uid} />
    </g>
  )
}

function TeePack({ c }) {
  const tees = [-28, -16, -6, 4, 14, 26]
  const fills = [c, '#d8b98a', c, PAPER, '#d8b98a', c]
  return (
    <g>
      {tees.map((a, i) => (
        <g key={i} transform={`translate(${170 + i * 12} 250) rotate(${a})`}>
          <path d="M-13 -150 Q0 -140 13 -150 L5 -136 L3 0 L0 12 L-3 0 L-5 -136 Z" style={{ fill: fills[i] }} stroke={INK} strokeOpacity="0.15" />
        </g>
      ))}
      <rect x="118" y="232" width="164" height="206" rx="10" fill="#d9c3a0" />
      <path d="M118 232 H282 L270 252 H130 Z" fill="#000" opacity="0.08" />
      <rect x="140" y="292" width="120" height="96" rx="8" fill={PAPER} />
      <BallMark x={200} y={322} r={12} fill={CORAL} />
      <Word x={200} y={356} size={13} fill={INK}>DIVOT &amp; CO</Word>
      <text x="200" y="374" textAnchor="middle" fontFamily="var(--font-mono)" fontSize="8.5" fill={INK} opacity="0.6" letterSpacing="1.5">BAMBOO TEES · 70MM</text>
    </g>
  )
}

function IronSet({ c, d }) {
  const nums = ['4', '5', '6', '7', '8', '9']
  return (
    <g>
      {nums.map((n, i) => {
        const x = 64 + i * 46
        const y = 180 + (i % 2) * 18
        const fill = i % 2 ? shade(c, 10) : c
        return (
          <g key={n}>
            <rect x={x} y={y} width="62" height="190" rx="28" style={{ fill }} stroke={shade(c, 22)} strokeWidth="2" />
            <rect x={x} y={y + 150} width="62" height="40" rx="12" style={{ fill: shade(c, 22) }} />
            <circle cx={x + 31} cy={y + 52} r="15" style={{ fill: d }} />
            <text x={x + 31} y={y + 58} textAnchor="middle" className="display" fontSize="16" style={{ fill: c }}>{n}</text>
          </g>
        )
      })}
      <BallMark x={200} y={420} r={10} fill={CORAL} />
    </g>
  )
}

function DivotTool({ c, logo, uid }) {
  return (
    <g transform="translate(200 250) rotate(-24)">
      <linearGradient id={`${uid}-steel`} x1="0" y1="0" x2="1" y2="0">
        <stop offset="0" stopColor="#8d949a" />
        <stop offset="0.5" stopColor="#eef0f1" />
        <stop offset="1" stopColor="#8d949a" />
      </linearGradient>
      <rect x="-36" y="10" width="20" height="160" rx="10" fill={`url(#${uid}-steel)`} />
      <rect x="16" y="10" width="20" height="160" rx="10" fill={`url(#${uid}-steel)`} />
      <rect x="-44" y="-4" width="88" height="34" rx="12" fill={`url(#${uid}-steel)`} />
      <rect x="-48" y="-128" width="96" height="134" rx="44" style={{ fill: c }} />
      <rect x="-48" y="-128" width="96" height="134" rx="44" style={{ fill: 'none', stroke: shade(c, 22) }} strokeWidth="3" />
      <circle cx="0" cy="-66" r="30" fill={`url(#${uid}-steel)`} />
      <BallMark x={0} y={-66} r={14} fill={logo} />
    </g>
  )
}

function Pouch({ c, d, logo }) {
  return (
    <g>
      <path d="M90 230 Q50 270 80 320" style={{ fill: 'none', stroke: shade(c, 18) }} strokeWidth="10" strokeLinecap="round" />
      <rect x="88" y="192" width="224" height="176" rx="24" style={{ fill: c }} />
      <rect x="88" y="192" width="224" height="34" rx="16" style={{ fill: shade(c, 12) }} />
      <line x1="104" y1="209" x2="296" y2="209" style={{ stroke: d }} strokeWidth="3" strokeDasharray="3 3" />
      <rect x="278" y="200" width="16" height="30" rx="4" style={{ fill: d }} />
      <circle cx="286" cy="238" r="6" style={{ fill: 'none', stroke: d }} strokeWidth="3" />
      <rect x="146" y="262" width="108" height="56" rx="12" style={{ fill: d }} />
      <BallMark x={172} y={290} r={12} fill={logo} />
      <text x="216" y="296" textAnchor="middle" className="display" fontSize="15" style={{ fill: c }}>D&amp;C</text>
      <rect x="100" y="240" width="200" height="116" rx="16" style={stitch(d)} />
    </g>
  )
}

const drawers = {
  driver: (p) => <Headcover {...p} tag="1" />,
  wood: (p) => <Headcover {...p} tag="3" small />,
  blade: BladeCover,
  mallet: MalletCover,
  cap: Cap,
  bucket: BucketHat,
  visor: Visor,
  standbag: (p) => <StandBag {...p} />,
  carrybag: (p) => <StandBag {...p} slim />,
  towel: Towel,
  balls: BallBox,
  markers: MarkerSet,
  tees: TeePack,
  irons: IronSet,
  divot: DivotTool,
  pouch: Pouch,
}

export default function ProductArt({ art, colour, detail = false, bg }) {
  const uid = useId().replace(/:/g, '')
  const c = hexOf(colour)
  const d = LIGHT.includes(colour) ? INK : PAPER
  const logo = colour === 'Coral' ? PAPER : CORAL
  const alt = colour === 'White' ? hexOf('Coral') : hexOf('White')
  const Draw = drawers[art]
  const background = bg ?? (detail ? tint(c, 78) : 'var(--paper-2)')

  return (
    <svg viewBox="0 0 400 500" preserveAspectRatio="xMidYMid slice" className="absolute inset-0 h-full w-full" aria-hidden="true">
      <rect width="400" height="500" style={{ fill: background, transition: 'fill 0.5s' }} />
      <g
        transform={detail ? 'translate(200 250) scale(1.45) rotate(-8) translate(-200 -250)' : undefined}
        style={{ filter: 'drop-shadow(0 8px 14px rgb(0 0 0 / 0.10))' }}
      >
        {!detail && <ellipse cx="200" cy="452" rx="130" ry="14" fill="#000" opacity="0.07" />}
        {Draw && <Draw c={c} d={d} logo={logo} uid={uid} alt={alt} />}
      </g>
    </svg>
  )
}
