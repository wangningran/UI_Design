import { useEffect, useState } from 'react'

// Preview-only palette switcher. Remove once a palette is chosen.
const themes = [
  { id: 'fairway', label: 'Fairway Lime', swatch: ['#0f3d2e', '#d4ff3a'] },
  { id: 'sky', label: 'Clubhouse Sky', swatch: ['#0f2a44', '#7cc8ff'] },
  { id: 'coral', label: 'Sunset Coral', swatch: ['#1f4d3a', '#ff6b4a'] },
]

const read = () => {
  try {
    return localStorage.getItem('theme') || 'fairway'
  } catch {
    return 'fairway'
  }
}

export default function ThemeSwitcher() {
  const [theme, setTheme] = useState(read)

  useEffect(() => {
    document.documentElement.dataset.theme = theme
    try {
      localStorage.setItem('theme', theme)
    } catch {
      /* storage unavailable — preview still works for this visit */
    }
  }, [theme])

  return (
    <div className="fixed bottom-5 left-5 z-40 flex items-center gap-1 rounded-full bg-ink/90 p-1.5 pr-3 text-paper shadow-lg backdrop-blur">
      {themes.map((t) => (
        <button
          key={t.id}
          onClick={() => setTheme(t.id)}
          title={t.label}
          aria-label={t.label}
          className={`flex h-8 w-8 items-center justify-center rounded-full transition-colors ${theme === t.id ? 'bg-paper/20' : 'hover:bg-paper/10'}`}
        >
          <span
            className="h-5 w-5 rounded-full"
            style={{ background: `linear-gradient(135deg, ${t.swatch[0]} 50%, ${t.swatch[1]} 50%)` }}
          />
        </button>
      ))}
      <span className="eyebrow ml-1 hidden sm:inline">{themes.find((t) => t.id === theme)?.label}</span>
    </div>
  )
}
