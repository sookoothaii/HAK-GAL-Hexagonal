/**
 * DEPRECATED - Backend switching is disabled
 * System now uses fixed backend on port 5002 (WRITE)
 * Port 5001 is kept as internal fallback only
 * 
 * This component is kept for reference but should not be used
 */

import React from 'react';
import { Badge } from '@/components/ui/badge';
import { Server } from 'lucide-react';

export const BackendSwitcher: React.FC = () => {
  // Component is deprecated - just return a status badge
  return (
    <Badge variant="outline" className="flex items-center gap-1 text-xs">
      <Server className="w-3 h-3" />
      Port 5002 (WRITE)
    </Badge>
  );
};

export default BackendSwitcher;