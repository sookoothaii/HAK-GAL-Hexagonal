# HAK-GAL Suite Frontend

## Installation

1. Öffnen Sie ein Terminal im `frontend_new` Verzeichnis
2. Führen Sie aus: `install.bat` oder `npm install`
3. Starten Sie den Development Server: `npm run dev`

## Migration der Komponenten

Die Komponenten aus dem alten Frontend können schrittweise migriert werden:

1. Kopieren Sie die Komponenten aus `frontend/src/components` nach `frontend_new/src/components`
2. Passen Sie die Import-Pfade an (verwenden Sie relative Imports statt @/)
3. Testen Sie jede Komponente einzeln

## Struktur

```
src/
├── components/       # UI Komponenten
├── hooks/           # Custom React Hooks
├── lib/             # Utility Functions
├── stores/          # Zustand Stores
├── App.tsx          # Haupt-Komponente
├── main.tsx         # Entry Point
└── index.css        # Global Styles
```

## Tech Stack

- **Vite 5.3.4** - Build Tool
- **React 18.3.1** - UI Library
- **TypeScript 5.5.3** - Type Safety
- **Tailwind CSS 3.4.11** - Styling
- **Zustand 5.0.6** - State Management
- **Socket.io-client 4.8.1** - WebSocket Communication
- **Recharts 2.12.7** - Charts
- **Radix UI** - Headless UI Components

## Features

- State-of-the-art Neuro-Symbolic Interface
- Real-time Governor Dashboard
- WebSocket Integration
- Scientific Dark Theme
- Responsive Design
