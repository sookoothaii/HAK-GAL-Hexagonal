// Virtual Scrolling Implementation for HAK-GAL Frontend
// Nach Artikel 2: Gezielte Befragung der Skalierungsgrenzen

import React, { useState, useEffect, useCallback } from 'react';
import { FixedSizeList } from 'react-window';
import { useGovernorStore } from '../stores/useGovernorStore';
import { Card } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';

interface Fact {
  id: number;
  statement: string;
  confidence?: number;
  source?: string;
}

const ITEMS_PER_PAGE = 100;
const ROW_HEIGHT = 80;

export const ScalableKnowledgeBase: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [displayedFacts, setDisplayedFacts] = useState<Fact[]>([]);
  const [filteredFacts, setFilteredFacts] = useState<Fact[]>([]);
  const [totalFacts, setTotalFacts] = useState(0);
  
  // Load facts with pagination
  const loadFacts = useCallback(async (page: number, query?: string) => {
    try {
      const response = await fetch(`/api/knowledge-base/page?page=${page}&limit=${ITEMS_PER_PAGE}${query ? `&query=${query}` : ''}`);
      const data = await response.json();
      
      setDisplayedFacts(data.facts);
      setTotalFacts(data.total);
      
      return data;
    } catch (error) {
      console.error('Error loading facts:', error);
      // Fallback to full load if pagination not available
      const response = await fetch('/api/knowledge-base/raw');
      const data = await response.json();
      
      let facts = data.facts || [];
      
      // Apply client-side filtering if needed
      if (query) {
        facts = facts.filter((f: Fact) => 
          f.statement.toLowerCase().includes(query.toLowerCase())
        );
      }
      
      // Client-side pagination
      const start = (page - 1) * ITEMS_PER_PAGE;
      const end = start + ITEMS_PER_PAGE;
      
      setFilteredFacts(facts);
      setDisplayedFacts(facts.slice(start, end));
      setTotalFacts(facts.length);
    }
  }, []);
  
  // Initial load
  useEffect(() => {
    loadFacts(1);
  }, [loadFacts]);
  
  // Search handler with debounce
  useEffect(() => {
    const timer = setTimeout(() => {
      loadFacts(1, searchQuery);
      setCurrentPage(1);
    }, 300);
    
    return () => clearTimeout(timer);
  }, [searchQuery, loadFacts]);
  
  // Row renderer for virtual scrolling
  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => {
    const fact = displayedFacts[index];
    
    if (!fact) return null;
    
    return (
      <div style={style} className="px-4 py-2">
        <Card className="p-3">
          <div className="flex justify-between items-start">
            <div className="flex-1">
              <span className="text-sm font-mono">{fact.statement}</span>
            </div>
            <div className="ml-4 flex gap-2">
              <Badge variant="outline">#{fact.id}</Badge>
              {fact.confidence && (
                <Badge variant={fact.confidence > 0.8 ? 'default' : 'secondary'}>
                  {(fact.confidence * 100).toFixed(0)}%
                </Badge>
              )}
            </div>
          </div>
        </Card>
      </div>
    );
  };
  
  // Pagination controls
  const totalPages = Math.ceil(totalFacts / ITEMS_PER_PAGE);
  
  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    loadFacts(page, searchQuery);
  };
  
  return (
    <div className="flex flex-col h-full">
      {/* Search Header */}
      <div className="p-4 border-b">
        <div className="flex gap-4 items-center">
          <Input
            type="search"
            placeholder="Search facts..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="max-w-md"
          />
          <div className="text-sm text-muted-foreground">
            {totalFacts.toLocaleString()} facts
            {searchQuery && ` matching "${searchQuery}"`}
          </div>
        </div>
      </div>
      
      {/* Virtual Scrolling List */}
      <div className="flex-1">
        <FixedSizeList
          height={600}
          itemCount={displayedFacts.length}
          itemSize={ROW_HEIGHT}
          width="100%"
          overscanCount={5}
        >
          {Row}
        </FixedSizeList>
      </div>
      
      {/* Pagination Footer */}
      <div className="p-4 border-t flex justify-between items-center">
        <div className="flex gap-2">
          <button
            onClick={() => handlePageChange(1)}
            disabled={currentPage === 1}
            className="px-3 py-1 border rounded disabled:opacity-50"
          >
            First
          </button>
          <button
            onClick={() => handlePageChange(currentPage - 1)}
            disabled={currentPage === 1}
            className="px-3 py-1 border rounded disabled:opacity-50"
          >
            Previous
          </button>
        </div>
        
        <div className="text-sm">
          Page {currentPage} of {totalPages}
        </div>
        
        <div className="flex gap-2">
          <button
            onClick={() => handlePageChange(currentPage + 1)}
            disabled={currentPage === totalPages}
            className="px-3 py-1 border rounded disabled:opacity-50"
          >
            Next
          </button>
          <button
            onClick={() => handlePageChange(totalPages)}
            disabled={currentPage === totalPages}
            className="px-3 py-1 border rounded disabled:opacity-50"
          >
            Last
          </button>
        </div>
      </div>
    </div>
  );
};
