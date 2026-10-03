import SocialAvatar, { avatarVariants } from './SocialAvatar'

// Preview sheet: each avatar as uploaded (square), as cropped (circle) and at feed size.
// `?export=<id>` renders a single 1080×1080 avatar for PNG export.
export default function SocialSheet() {
  const exportId = new URLSearchParams(location.search).get('export')
  if (exportId) return <SocialAvatar variant={exportId} size={1080} />

  return (
    <main className="container-x py-12 lg:py-20">
      <p className="eyebrow text-muted">Divot &amp; Co · Social avatars</p>
      <h1 className="display mt-5 text-[clamp(2.2rem,6vw,5rem)]">Profile pictures</h1>
      <p className="mt-6 max-w-xl text-[15px] leading-relaxed text-ink-2">
        Upload the square 1080×1080 PNG. Platforms crop it to a circle, so all artwork sits inside the
        centre. Right-hand sizes show how it reads in a feed.
      </p>

      <div className="mt-12 divide-y divide-line border-y border-line">
        {avatarVariants.map((v) => (
          <section key={v.id} className="flex flex-wrap items-center gap-8 py-10">
            <div className="w-40">
              <p className="display text-lg">{v.name}</p>
              <p className="eyebrow mt-2 text-muted">divot-avatar-{v.id}.png</p>
            </div>
            <figure className="text-center">
              <div className="ring-1 ring-line"><SocialAvatar variant={v.id} size={200} /></div>
              <figcaption className="eyebrow mt-3 text-muted">Upload (square)</figcaption>
            </figure>
            <figure className="text-center">
              <SocialAvatar variant={v.id} size={200} round />
              <figcaption className="eyebrow mt-3 text-muted">Profile (circle)</figcaption>
            </figure>
            <figure className="flex flex-col items-center">
              <div className="flex items-end gap-5">
                <SocialAvatar variant={v.id} size={80} round />
                <SocialAvatar variant={v.id} size={40} round />
                <SocialAvatar variant={v.id} size={32} round />
              </div>
              <figcaption className="eyebrow mt-3 text-muted">Feed · 80 / 40 / 32 px</figcaption>
            </figure>
          </section>
        ))}
      </div>
    </main>
  )
}
