// Renders a product/editorial image, or a labelled placeholder while no
// photography has been supplied. Keeps the aspect ratio so layout never shifts.
export default function ImageSlot({ src, alt = '', ratio = '4 / 5', label = 'Product image', className = '' }) {
  return (
    <div className={`relative w-full overflow-hidden ${className}`} style={{ aspectRatio: ratio }}>
      {src ? (
        <img src={src} alt={alt} loading="lazy" className="absolute inset-0 h-full w-full object-cover" />
      ) : (
        <div className="placeholder-hatch absolute inset-0 flex items-center justify-center">
          <span className="eyebrow text-muted">
            {label} · {ratio.replace(/\s/g, '')}
          </span>
        </div>
      )}
    </div>
  )
}
