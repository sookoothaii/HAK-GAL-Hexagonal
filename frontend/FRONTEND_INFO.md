# HAK_GAL Frontend package.json
# Version: 1.0.0
# Generated: 2025-08-23

This frontend requires the following dependencies:

## Core React & Build Tools
- React 18.3
- Vite 5.4
- TypeScript 5.5

## UI Framework
- Tailwind CSS 3.4
- Radix UI Components
- Shadcn/ui Components
- Framer Motion

## State Management & Routing
- React Router DOM 6.26
- React Hook Form 7.53
- @tanstack/react-query 5.55

## Data Visualization
- D3.js 7.9
- Recharts 2.13

## API & WebSocket
- Axios 1.7
- Socket.io-client 4.7

## Development Tools
- ESLint + React Plugin
- PostCSS
- Autoprefixer

## Installation
```bash
cd frontend
npm install
```

## Scripts
- `npm run dev` - Start development server (Vite)
- `npm run build` - Build for production
- `npm run lint` - Run ESLint
- `npm run preview` - Preview production build

## Environment Variables
Create `.env.local` with:
```
VITE_API_URL=http://localhost:5002
VITE_WS_URL=ws://localhost:5002
```

## Notes
- Node modules NOT included in backup (run npm install)
- Dist folder NOT included (run npm run build)
- Uses Vite for fast HMR development