const base = { width: 18, height: 18, fill: 'none', stroke: 'currentColor', strokeWidth: 1.4, viewBox: '0 0 24 24' }

export const SearchIcon = (p) => (
  <svg {...base} {...p}><circle cx="11" cy="11" r="6.5" /><path d="m20 20-4.2-4.2" /></svg>
)
export const UserIcon = (p) => (
  <svg {...base} {...p}><circle cx="12" cy="8" r="3.5" /><path d="M5 20c1.2-3.5 4-5 7-5s5.8 1.5 7 5" /></svg>
)
export const BagIcon = (p) => (
  <svg {...base} {...p}><path d="M5 8h14l-1 12H6L5 8Z" /><path d="M9 8a3 3 0 0 1 6 0" /></svg>
)
export const MenuIcon = (p) => (
  <svg {...base} {...p}><path d="M4 8h16M4 16h16" /></svg>
)
export const CloseIcon = (p) => (
  <svg {...base} {...p}><path d="m6 6 12 12M18 6 6 18" /></svg>
)
export const PlusIcon = (p) => (
  <svg {...base} {...p}><path d="M12 5v14M5 12h14" /></svg>
)
export const ArrowIcon = (p) => (
  <svg {...base} {...p}><path d="M5 12h14m-5-5 5 5-5 5" /></svg>
)
