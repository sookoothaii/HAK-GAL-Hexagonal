// TrustAnalysisWrapper.tsx - Enhanced with Knowledge Base integration
import React, { useEffect, useState } from 'react';
import TrustScoreCard, { TrustComponents } from './TrustScoreCard';
import { useHRMIntegration } from '@/hooks/useHRMIntegration';
import { api } from '@/services/api';

interface TrustAnalysisWrapperProps {
  query: string;
  response: string;
  sources?: any[];
}

interface KBSearchResult {
  query: string;
  results: Array<{
    id: number;
    statement: string;
    confidence?: number;
  }>;
  count: number;
}

export const TrustAnalysisWrapper: React.FC<TrustAnalysisWrapperProps> = ({
  query,
  response,
  sources = []
}) => {
  const { queryHRM } = useHRMIntegration();
  const [kbFacts, setKbFacts] = useState<any[]>([]);
  const [trustComponents, setTrustComponents] = useState<TrustComponents>({
    neuralConfidence: 0,
    factualAccuracy: 0.3,  // Start low until verified
    sourceQuality: 0.1,
    consensus: 0.5,
    humanVerified: false,
    ethicalAlignment: 0.7
  });
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        // 1. Search Knowledge Base for relevant facts
        const searchResponse = await fetch('/api/search', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            query: query, 
            limit: 20 
          })
        });
        
        if (searchResponse.ok) {
          const kbData: KBSearchResult = await searchResponse.json();
          setKbFacts(kbData.results || []);
          
          // 2. Get HRM confidence
          const hrmResult = await queryHRM(query);
          
          // 3. Calculate real trust metrics based on KB and HRM
          const hasKbSupport = kbData.count > 0;
          const kbRelevance = Math.min(kbData.count / 10, 1); // More facts = higher relevance
          
          setTrustComponents({
            neuralConfidence: hrmResult.confidence,
            factualAccuracy: hasKbSupport ? 0.7 + (kbRelevance * 0.3) : 0.3,
            sourceQuality: hasKbSupport ? 0.6 + (kbRelevance * 0.3) : 0.1,
            consensus: (hrmResult.confidence + (hasKbSupport ? 0.8 : 0.2)) / 2,
            humanVerified: false,
            ethicalAlignment: 0.7
          });
          
          console.log(`📊 KB Search: Found ${kbData.count} relevant facts for query "${query}"`);
        }
      } catch (error) {
        console.error('Error fetching KB data:', error);
      }
    };
    
    if (query) {
      fetchData();
    }
  }, [query]);
  
  // Combine KB facts with any provided sources
  const allSources = [...sources, ...kbFacts.map(fact => ({
    type: 'kb_fact',
    content: fact.statement,
    confidence: fact.confidence || 0.8
  }))];
  
  return (
    <div>
      <TrustScoreCard
        query={query}
        response={response}
        components={trustComponents}
        sources={allSources}
      />
      {kbFacts.length > 0 && (
        <div className="mt-2 text-xs text-gray-500">
          📚 Using {kbFacts.length} facts from Knowledge Base (total: 5,953)
        </div>
      )}
    </div>
  );
};

export default TrustAnalysisWrapper;
