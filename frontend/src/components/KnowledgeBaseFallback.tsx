// Fallback Knowledge Base Component (works without react-window)
import React, { useState, useEffect } from 'react';
import { Card } from '../ui/card';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { ChevronLeft, ChevronRight } from 'lucide-react';

interface Fact {
  id: number;
  statement: string;
  confidence?: number;
  source?: string;
}

export const KnowledgeBaseFallback: React.FC = () => {
  const [facts, setFacts] = useState<Fact[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalFacts, setTotalFacts] = useState(0);
  const [loading, setLoading] = useState(false);
  
  const ITEMS_PER_PAGE = 50;
  
  useEffect(() => {
    loadFacts();
  }, [currentPage, searchQuery]);
  
  const loadFacts = async () => {
    setLoading(true);
    try {
      // Try paginated endpoint first
      const url = searchQuery 
        ? `/api/knowledge-base/page?page=${currentPage}&limit=${ITEMS_PER_PAGE}&query=${encodeURIComponent(searchQuery)}`
        : `/api/knowledge-base/page?page=${currentPage}&limit=${ITEMS_PER_PAGE}`;
        
      const response = await fetch(url);
      
      if (response.ok) {
        const data = await response.json();
        setFacts(data.facts || []);
        setTotalFacts(data.total || 0);
      } else {
        // Fallback to raw endpoint
        console.log('Pagination not available, using raw endpoint');
        const rawResponse = await fetch('/api/knowledge-base/raw');
        const rawData = await rawResponse.json();
        
        let allFacts = rawData.facts || [];
        setTotalFacts(allFacts.length);
        
        // Client-side search
        if (searchQuery) {
          allFacts = allFacts.filter((f: Fact) =>
            f.statement.toLowerCase().includes(searchQuery.toLowerCase())
          );
        }
        
        // Client-side pagination
        const start = (currentPage - 1) * ITEMS_PER_PAGE;
        const paginatedFacts = allFacts.slice(start, start + ITEMS_PER_PAGE);
        setFacts(paginatedFacts);
      }
    } catch (error) {
      console.error('Error loading facts:', error);
      setFacts([]);
    } finally {
      setLoading(false);
    }
  };
  
  const totalPages = Math.ceil(totalFacts / ITEMS_PER_PAGE);
  
  return (
    <div className="flex flex-col h-full">
      {/* Search Header */}
      <div className="p-4 border-b">
        <div className="flex gap-4 items-center">
          <Input
            type="search"
            placeholder="Search facts..."
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setCurrentPage(1);
            }}
            className="max-w-md"
          />
          <div className="text-sm text-muted-foreground">
            {totalFacts.toLocaleString()} facts total
            {searchQuery && ` matching "${searchQuery}"`}
          </div>
        </div>
      </div>
      
      {/* Facts List */}
      <div className="flex-1 overflow-auto p-4">
        {loading ? (
          <div className="text-center py-8 text-muted-foreground">Loading...</div>
        ) : facts.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            No facts found {searchQuery && `matching "${searchQuery}"`}
          </div>
        ) : (
          <div className="space-y-2">
            {facts.map((fact) => (
              <Card key={fact.id} className="p-3">
                <div className="flex justify-between items-start">
                  <span className="text-sm font-mono flex-1">{fact.statement}</span>
                  <div className="ml-4 flex gap-2">
                    <Badge variant="outline">#{fact.id}</Badge>
                    {fact.confidence !== undefined && (
                      <Badge variant={fact.confidence > 0.8 ? 'default' : 'secondary'}>
                        {(fact.confidence * 100).toFixed(0)}%
                      </Badge>
                    )}
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
      
      {/* Pagination Footer */}
      <div className="p-4 border-t flex justify-between items-center">
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setCurrentPage(1)}
            disabled={currentPage === 1}
          >
            First
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
            disabled={currentPage === 1}
          >
            <ChevronLeft className="h-4 w-4" />
            Previous
          </Button>
        </div>
        
        <div className="text-sm text-muted-foreground">
          Page {currentPage} of {totalPages || 1}
        </div>
        
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setCurrentPage(currentPage + 1)}
            disabled={currentPage >= totalPages}
          >
            Next
            <ChevronRight className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setCurrentPage(totalPages)}
            disabled={currentPage >= totalPages}
          >
            Last
          </Button>
        </div>
      </div>
    </div>
  );
};

export default KnowledgeBaseFallback;
