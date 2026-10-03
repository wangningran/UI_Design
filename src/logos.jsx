import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import LogoConcepts from './components/brand/LogoConcepts.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <LogoConcepts />
  </StrictMode>,
)
