import React from 'react'
import { createRoot } from 'react-dom/client'
import { BookingSystem } from './app.jsx'
import './style.css'

const root = createRoot(document.getElementById('root'))
root.render(
    <React.StrictMode>
        <BookingSystem />
    </React.StrictMode>
)