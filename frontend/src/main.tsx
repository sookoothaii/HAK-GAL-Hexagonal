import "./utils/consoleSuppressor";
import React from 'react'
import ReactDOM from 'react-dom/client'
// import App from './App.tsx' // Old UI
import App from './ProApp.tsx' // Professional UI
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
