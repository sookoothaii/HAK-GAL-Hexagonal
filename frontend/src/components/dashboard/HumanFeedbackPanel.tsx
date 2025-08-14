// src/components/dashboard/HumanFeedbackPanel.tsx
import React from 'react';
import { useGovernorStore } from '@/stores/useGovernorStore';
import { useGovernorSocket } from '@/hooks/useGovernorSocket'; // Corrected import

const HumanFeedbackPanel = () => {
  const pendingTheses = useGovernorStore(state => state.pendingTheses);
  const wsService = useGovernorSocket(); // Use the hook to get the service instance

  const handleApprove = (thesisId: string) => {
    wsService.sendThesisFeedback(thesisId, 'approve');
  };

  const handleReject = (thesisId: string) => {
    wsService.sendThesisFeedback(thesisId, 'reject');
  };

  return (
    <div className="h-full w-full p-4 rounded-lg border border-border bg-card overflow-hidden flex flex-col">
      <h3 className="text-lg font-semibold mb-4">Human Feedback Required</h3>
      <div className="flex-1 space-y-3 overflow-y-auto">
        {pendingTheses.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-sm text-muted-foreground">No theses pending review</p>
            <p className="text-xs text-muted-foreground mt-2">
              The system will notify you when new theses require validation
            </p>
          </div>
        ) : (
          pendingTheses.map(thesis => (
            <div key={thesis.id} className="p-3 rounded-md border border-border bg-background">
              <div className="mb-2">
                <div className="text-sm text-muted-foreground mb-1">LLM Hypothesis:</div>
                <div className="text-sm">{thesis.llmHypothesis}</div>
              </div>
              <div className="mb-3">
                <div className="text-sm text-muted-foreground mb-1">Logical Thesis:</div>
                <div className="text-sm font-mono bg-muted/50 p-2 rounded">{thesis.logicalThesis}</div>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => handleApprove(thesis.id)}
                  className="px-3 py-1 text-sm rounded bg-success text-success-foreground hover:bg-success/90 transition-colors"
                >
                  Approve
                </button>
                <button
                  onClick={() => handleReject(thesis.id)}
                  className="px-3 py-1 text-sm rounded bg-destructive text-destructive-foreground hover:bg-destructive/90 transition-colors"
                >
                  Reject
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default HumanFeedbackPanel;
