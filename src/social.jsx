import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import SocialSheet from './components/brand/SocialSheet.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <SocialSheet />
  </StrictMode>,
)
