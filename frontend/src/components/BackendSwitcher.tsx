import React from 'react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Badge } from '@/components/ui/badge';
import { Server, ChevronDown, Check } from 'lucide-react';
import { BACKENDS, getActiveBackend, setActiveBackend } from '@/config/backends';
import { toast } from 'sonner';

export const BackendSwitcher: React.FC = () => {
  const currentBackend = getActiveBackend();
  
  const handleSwitch = (backendKey: 'original' | 'hexagonal') => {
    if (backendKey === currentBackend.type) return;
    
    toast.info(`Switching to ${BACKENDS[backendKey].name}...`, {
      description: 'The page will reload to apply changes.',
    });
    
    setTimeout(() => {
      setActiveBackend(backendKey);
    }, 1000);
  };
  
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" className="gap-2">
          <Server className="h-4 w-4" />
          <span className="hidden sm:inline">{currentBackend.name}</span>
          <Badge variant="secondary" className="ml-2">
            Port {currentBackend.port}
          </Badge>
          <ChevronDown className="h-4 w-4 ml-1" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-80">
        <DropdownMenuLabel>Select Backend System</DropdownMenuLabel>
        <DropdownMenuSeparator />
        
        {Object.entries(BACKENDS).map(([key, backend]) => (
          <DropdownMenuItem
            key={key}
            onClick={() => handleSwitch(key as 'original' | 'hexagonal')}
            className="flex flex-col items-start gap-1 p-3"
          >
            <div className="flex items-center justify-between w-full">
              <div className="flex items-center gap-2">
                <span className="font-medium">{backend.name}</span>
                {currentBackend.type === backend.type && (
                  <Check className="h-4 w-4 text-primary" />
                )}
              </div>
              <Badge variant="outline">Port {backend.port}</Badge>
            </div>
            <div className="text-xs text-muted-foreground">
              {backend.stats.architecture}
            </div>
            <div className="flex gap-1 mt-1">
              <Badge variant="secondary" className="text-xs">
                {backend.stats.facts} facts
              </Badge>
              <Badge variant="secondary" className="text-xs">
                {backend.stats.responseTime}
              </Badge>
            </div>
          </DropdownMenuItem>
        ))}
        
        <DropdownMenuSeparator />
        <div className="px-3 py-2">
          <p className="text-xs text-muted-foreground">
            Switching backends will reload the application to ensure proper connection.
          </p>
        </div>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

export default BackendSwitcher;
