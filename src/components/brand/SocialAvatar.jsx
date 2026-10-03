import { Ball } from './Marks'

// Square social-media avatars built from the Ball O logo.
// Content stays inside the central circle so platform crops never clip it.
export const avatarVariants = [
  { id: 'stacked', name: 'Stacked wordmark', bg: 'var(--paper)', fg: 'var(--ink)', amp: 'var(--accent)', ball: 'var(--accent)' },
  { id: 'forest', name: 'Stacked · forest', bg: 'var(--night)', fg: 'var(--paper)', amp: 'var(--accent)', ball: 'var(--accent)' },
  { id: 'coral', name: 'Stacked · coral', bg: 'var(--accent)', fg: 'var(--ink)', amp: 'var(--paper)', ball: 'var(--paper)' },
  { id: 'ball', name: 'Ball icon', bg: 'var(--night)', ball: 'var(--accent)', iconOnly: true },
]

export default function SocialAvatar({ variant, size = 320, round = false }) {
  const v = avatarVariants.find((a) => a.id === variant)
  return (
    <div
      className={`relative flex shrink-0 items-center justify-center overflow-hidden ${round ? 'rounded-full' : ''}`}
      style={{ width: size, height: size, background: v.bg, color: v.fg }}
    >
      {v.iconOnly ? (
        <span style={{ fontSize: size * 0.62 }} className="flex">
          <Ball fill={v.ball} />
        </span>
      ) : (
        <span
          className="display flex flex-col items-center leading-[0.86]"
          style={{ fontSize: size * 0.2 }}
        >
          <span className="flex items-center">
            DIV<Ball className="mx-[0.02em]" fill={v.ball} />T
          </span>
          <span className="mt-[0.06em]">
            <span style={{ color: v.amp }}>&amp;</span> CO
          </span>
        </span>
      )}
    </div>
  )
}
