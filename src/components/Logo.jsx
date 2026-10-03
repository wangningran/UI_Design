export default function Logo({ className = '' }) {
  return (
    <span className={`display inline-flex items-center gap-1.5 ${className}`}>
      Studio
      <span className="inline-block h-[0.42em] w-[0.42em] rounded-full bg-accent ring-1 ring-ink/10" />
      Golf
    </span>
  )
}
