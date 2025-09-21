// V3 - Fixed for existing pages with proper React imports
import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from '@/components/theme-provider';
import { AnimatePresence, motion } from 'framer-motion';
import { Toaster } from "sonner";
import { useStoreBridge } from '@/core/bridge/StoreBridge';
import { EnterpriseErrorBoundary as DashboardErrorBoundary } from '@/components/EnterpriseErrorBoundary';
import { initializeDefaults } from '@/services/defaultsService';

// Import ONLY pages that actually exist
import ProDashboardEnhanced from '@/pages/ProDashboardEnhanced'; // ENHANCED NO-SCROLL VERSION
import ProGovernorControl from '@/pages/ProGovernorControl';
import ProKnowledgeList from '@/pages/ProKnowledgeList';
import ProSystemMonitoring from '@/pages/ProSystemMonitoring';
import ProKnowledgeStats from '@/pages/ProKnowledgeStats';
import ProLLMManagement from '@/pages/ProLLMManagement';
import ProSettingsEnhanced from '@/pages/ProSettingsEnhanced';
import ProUnifiedQuery from '@/pages/ProUnifiedQuery';
import ProEngineControl from '@/pages/ProEngineControl';
import WorkflowPage from '@/pages/WorkflowFixed';
import WorkflowPro from '@/pages/WorkflowPro';
import HRMDashboard from '@/pages/HRMDashboard';
import ProNavigation from '@/components/ProNavigation';
import KnowledgeGraphVisualization from '@/components/interaction/KnowledgeGraphVisualization';
import HallucinationPrevention from '@/components/HallucinationPrevention/HallucinationPrevention';

function AppContent() {
  // Use existing store bridge - it handles WebSocket connection
  useStoreBridge();
  
  useEffect(() => {
    // Load dynamic defaults from backend
    initializeDefaults().catch(console.error);
    
    // Force correct status display - using real backend data
    console.log('[Dashboard] Using real backend data via WebSocket');
    
    // Optional: Check if we're connected after a delay
    const timer = setTimeout(() => {
      console.log('[Dashboard] Dashboard ready');
    }, 500);

    return () => clearTimeout(timer);
  }, []);

  return (
    <AnimatePresence mode="wait">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.3 }}
        className="h-screen bg-background flex flex-row overflow-hidden"
      >
        {/* Navigation LINKS als Sidebar */}
        <ProNavigation />
        {/* Main Content RECHTS */}
        <main className="flex-1 overflow-hidden">
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={
              <DashboardErrorBoundary name="Dashboard">
                <ProDashboardEnhanced />
              </DashboardErrorBoundary>
            } />
            <Route path="/governor" element={<ProGovernorControl />} />
            <Route path="/knowledge" element={<ProKnowledgeList />} />
            <Route path="/knowledge/list" element={<ProKnowledgeList />} />
            <Route path="/knowledge/stats" element={<ProKnowledgeStats />} />
            <Route path="/knowledge/graph" element={<KnowledgeGraphVisualization />} />
            <Route path="/graph" element={<KnowledgeGraphVisualization />} />
            <Route path="/hrm" element={<HRMDashboard />} />
            <Route path="/hallucination-prevention" element={<HallucinationPrevention />} />
            <Route path="/system" element={<ProSystemMonitoring />} />
            <Route path="/monitoring" element={<ProSystemMonitoring />} />
            <Route path="/stats" element={<ProKnowledgeStats />} />
            <Route path="/llm" element={<ProLLMManagement />} />
            <Route path="/settings" element={<ProSettingsEnhanced />} />
            {/* Legacy workflow - hidden but still accessible via direct URL */}
            <Route path="/workflow-legacy" element={<WorkflowPage />} />
            {/* Main workflow - the professional version */}
            <Route path="/workflow" element={<WorkflowPro />} />
            <Route path="/workflow-pro" element={<WorkflowPro />} />  {/* Redirect for compatibility */}
            <Route path="/query" element={<ProUnifiedQuery />} />
            <Route path="/engines" element={<ProEngineControl />} />
            {/* Redirect all unknown routes to dashboard */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </main>
      </motion.div>
    </AnimatePresence>
  );
}

export default function App() {
  return (
    <DashboardErrorBoundary name="Application">
      <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
        <Router>
          <AppContent />
          <Toaster />
        </Router>
      </ThemeProvider>
    </DashboardErrorBoundary>
  );
}