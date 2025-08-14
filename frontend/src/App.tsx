import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@/components/theme-provider';
import { useGovernorSocket } from '@/hooks/useGovernorSocket';
import Navigation from '@/components/Navigation';

// Pages
import DashboardPage from '@/pages/DashboardPage';
import QueryPage from '@/pages/QueryPage';
import KnowledgePage from '@/pages/KnowledgePage';
import GovernorPage from '@/pages/GovernorPage';
import EnginesPage from '@/pages/EnginesPage';

function AppContent() {
  // Establish WebSocket connection
  useGovernorSocket();

  return (
    <div className="h-screen w-screen bg-background text-foreground flex">
      {/* Sidebar Navigation */}
      <div className="w-64 h-full">
        <Navigation />
      </div>
      
      {/* Main Content Area */}
      <div className="flex-1 h-full overflow-hidden">
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/query" element={<QueryPage />} />
          <Route path="/knowledge" element={<KnowledgePage />} />
          <Route path="/governor" element={<GovernorPage />} />
          <Route path="/engines" element={<EnginesPage />} />
        </Routes>
      </div>
    </div>
  );
}

function App() {
  return (
    <ThemeProvider defaultTheme="dark" storageKey="hak-gal-theme">
      <Router>
        <AppContent />
      </Router>
    </ThemeProvider>
  );
}

export default App;
