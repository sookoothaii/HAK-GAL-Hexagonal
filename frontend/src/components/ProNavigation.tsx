import React, { useEffect, useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { useGovernorStore } from '@/stores/useGovernorStore';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard,
  Terminal,
  Brain,
  Settings,
  Activity,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  AlertCircle,
  CheckCircle2,
  Zap,
  Database,
  Network,
  BarChart3,
  Cpu
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { CURRENT_BACKEND, setActiveBackend, BACKENDS, getActiveBackend } from '@/config/backends';

interface NavItem {
  path: string;
  label: string;
  icon: React.ReactNode;
  badge?: string;
  description?: string;
  subItems?: NavItem[];
}

const ProNavigation: React.FC = () => {
  const location = useLocation();
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [hoveredItem, setHoveredItem] = useState<string | null>(null);
  const [expandedItems, setExpandedItems] = useState<string[]>(['/knowledge']);
  
  // Store subscriptions
  const isConnected = useGovernorStore(state => state.isConnected);
  const systemStatus = useGovernorStore(state => state.systemStatus);
  const governor = useGovernorStore(state => state.governor);
  const engines = useGovernorStore(state => state.engines);
  const kbMetrics = useGovernorStore(state => state.kb.metrics);
  
  // Calculate active engines
  const activeEngines = engines.filter(e => e.status === 'running').length;

  // Initial KB-FactCount nachladen, falls 0
  useEffect(() => {
    const active = getActiveBackend();
    const baseUrl = active.apiUrl;
    const isHex = /5001/.test(baseUrl) || /hex/i.test(active?.name || '');
    if ((kbMetrics?.factCount || 0) === 0) {
      (async () => {
        try {
          if (isHex) {
            const r = await fetch(`${baseUrl}/api/facts/count`);
            if (r.ok) {
              const d = await r.json();
              useGovernorStore.getState().handleKbUpdate({ metrics: { factCount: d.count || 0 } });
            }
          } else {
            const r2 = await fetch(`${baseUrl}/api/knowledge-base/status`);
            if (r2.ok) {
              const d2 = await r2.json();
              const count = d2?.knowledge_base_facts || d2?.factCount || 0;
              useGovernorStore.getState().handleKbUpdate({ metrics: { factCount: count } });
            }
          }
        } catch {}
      })();
    }
  }, []);
  
  // Navigation items - CLEANED & FOCUSED
  const navItems: NavItem[] = [
    {
      path: '/dashboard',
      label: 'Neurosymbolic Dashboard',
      icon: <LayoutDashboard className="w-4 h-4" />,
      description: 'System overview & integration'
    },
    {
      path: '/query',
      label: 'Query Interface',
      icon: <Terminal className="w-4 h-4" />,
      description: 'Neural + Symbolic reasoning',
      badge: 'DUAL'
    },
    {
      path: '/knowledge',
      label: 'Knowledge Base',
      icon: <Brain className="w-4 h-4" />,
      description: `${(kbMetrics?.factCount || 0).toLocaleString()} facts`,
      subItems: [
            {
              path: '/knowledge/list',
              label: 'Facts (Paginated)',
              icon: <Database className="w-4 h-4" />
            },
        {
          path: '/knowledge/graph',
          label: 'Graph Visualization',
          icon: <Network className="w-4 h-4" />
        },
        {
          path: '/knowledge/stats',
          label: 'Statistics',
          icon: <BarChart3 className="w-4 h-4" />
        }
      ]
    },
    // {
    //   path: '/workflow',
    //   label: 'Workflow (MVP)',
    //   icon: <Network className="w-4 h-4" />,
    //   description: 'Visual MCP orchestration'
    // },
    {
      path: '/workflow-pro',
      label: 'Workflow',  // Renamed to just "Workflow"
      icon: <Network className="w-4 h-4" />,
      description: 'Professional workflow editor'
    },
    {
      path: '/governor',
      label: 'Strategic Governor',
      icon: <Cpu className="w-4 h-4" />,
      description: governor.running ? 'Active' : 'Paused',
      badge: governor.running ? 'ON' : undefined
    },
    {
      path: '/monitoring',
      label: 'System Monitoring',
      icon: <Activity className="w-4 h-4" />,
      description: 'Performance & health'
    },
    {
      path: '/settings',
      label: 'Settings',
      icon: <Settings className="w-4 h-4" />,
      description: 'Configuration'
    }
  ];

  const getStatusIcon = () => {
    if (!isConnected) return <AlertCircle className="w-3 h-3" />;
    if (systemStatus === 'operational') return <CheckCircle2 className="w-3 h-3" />;
    if (systemStatus === 'degraded') return <Activity className="w-3 h-3" />;
    return <AlertCircle className="w-3 h-3" />;
  };

  const getStatusColor = () => {
    if (!isConnected) return 'text-destructive';
    if (systemStatus === 'operational') return 'text-green-500';
    if (systemStatus === 'degraded') return 'text-yellow-500';
    return 'text-destructive';
  };

  const toggleExpanded = (path: string) => {
    setExpandedItems(prev => 
      prev.includes(path) 
        ? prev.filter(p => p !== path)
        : [...prev, path]
    );
  };

  return (
    <TooltipProvider>
      <motion.nav
        initial={false}
        animate={{ width: isCollapsed ? '4rem' : '16rem' }}
        transition={{ duration: 0.3, ease: 'easeInOut' }}
        className="h-full bg-card border-r border-border flex flex-col relative"
      >
        {/* Header */}
        <div className="p-4 border-b border-border">
          <motion.div
            initial={false}
            animate={{ opacity: isCollapsed ? 0 : 1 }}
            transition={{ duration: 0.2 }}
          >
            {!isCollapsed && (
              <div>
                <h1 className="text-lg font-bold bg-gradient-to-r from-primary to-purple-500 bg-clip-text text-transparent flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-primary" />
                  HAK-GAL Suite
                </h1>
                <p className="text-xs text-muted-foreground mt-1">
                  Neurosymbolic AI Platform
                </p>
              </div>
            )}
          </motion.div>
          
          {/* Status Indicator */}
          <div className={cn(
            "mt-3 flex items-center gap-2",
            isCollapsed && "justify-center"
          )}>
            <Tooltip>
              <TooltipTrigger>
                <div className={cn("transition-colors", getStatusColor())}>
                  {getStatusIcon()}
                </div>
              </TooltipTrigger>
              <TooltipContent side="right">
                <p>System: {systemStatus}</p>
                <p>WebSocket: {isConnected ? 'Connected' : 'Disconnected'}</p>
                <p>Backend: {CURRENT_BACKEND.name}</p>
              </TooltipContent>
            </Tooltip>
            
            {!isCollapsed && (
              <div className="flex items-center gap-2 flex-1">
                <span className="text-xs text-muted-foreground">
                  {systemStatus.toUpperCase()}
                </span>
                {governor?.running && (
                  <Badge variant="outline" className="text-xs px-1.5 py-0">
                    <Zap className="w-3 h-3 mr-1" />
                    Learning
                  </Badge>
                )}
              </div>
            )}
          </div>
        </div>
        
        {/* Navigation Items */}
        <ScrollArea className="flex-1">
          <div className="p-2">
            <AnimatePresence>
              {navItems.map((item) => (
                <div key={item.path}>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <NavLink
                        to={item.path}
                        onClick={() => item.subItems && toggleExpanded(item.path)}
                        className={({ isActive }) =>
                          cn(
                            "group flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-200 relative",
                            isActive && !item.subItems
                              ? "bg-primary/10 text-primary font-medium"
                              : "hover:bg-muted/50 text-muted-foreground hover:text-foreground",
                            isCollapsed && "justify-center px-2"
                          )
                        }
                        onMouseEnter={() => setHoveredItem(item.path)}
                        onMouseLeave={() => setHoveredItem(null)}
                      >
                        {/* Active Indicator */}
                        {location.pathname === item.path && (
                          <motion.div
                            layoutId="activeIndicator"
                            className="absolute left-0 w-1 h-6 bg-primary rounded-r-full"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                          />
                        )}
                        
                        {/* Icon with animation */}
                        <motion.div
                          animate={{
                            scale: hoveredItem === item.path ? 1.1 : 1,
                            rotate: hoveredItem === item.path ? 5 : 0
                          }}
                          transition={{ duration: 0.2 }}
                        >
                          {item.icon}
                        </motion.div>
                        
                        {/* Label and description */}
                        {!isCollapsed && (
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between">
                              <span className="truncate">{item.label}</span>
                              {item.badge && (
                                <Badge 
                                  variant={item.badge === 'DUAL' ? 'default' : 'secondary'}
                                  className="ml-auto text-xs px-1.5 py-0"
                                >
                                  {item.badge}
                                </Badge>
                              )}
                            </div>
                            {item.description && hoveredItem === item.path && (
                              <motion.p
                                initial={{ opacity: 0, y: -5 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -5 }}
                                className="text-xs text-muted-foreground truncate"
                              >
                                {item.description}
                              </motion.p>
                            )}
                          </div>
                        )}
                        
                        {/* Expand indicator for subitems */}
                        {!isCollapsed && item.subItems && (
                          <ChevronRight className={cn(
                            "w-4 h-4 transition-transform",
                            expandedItems.includes(item.path) && "rotate-90"
                          )} />
                        )}
                      </NavLink>
                    </TooltipTrigger>
                    {isCollapsed && (
                      <TooltipContent side="right">
                        <p>{item.label}</p>
                        {item.description && (
                          <p className="text-xs text-muted-foreground">{item.description}</p>
                        )}
                      </TooltipContent>
                    )}
                  </Tooltip>
                  
                  {/* Subitems */}
                  {!isCollapsed && item.subItems && expandedItems.includes(item.path) && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      transition={{ duration: 0.2 }}
                      className="ml-4 mt-1"
                    >
                      {item.subItems.map(subItem => (
                        <NavLink
                          key={subItem.path}
                          to={subItem.path}
                          className={({ isActive }) =>
                            cn(
                              "flex items-center gap-2 px-3 py-1.5 rounded-md text-xs transition-colors",
                              isActive
                                ? "bg-primary/10 text-primary"
                                : "hover:bg-muted/50 text-muted-foreground hover:text-foreground"
                            )
                          }
                        >
                          {subItem.icon}
                          <span>{subItem.label}</span>
                        </NavLink>
                      ))}
                    </motion.div>
                  )}
                </div>
              ))}
            </AnimatePresence>
          </div>
        </ScrollArea>
        
        {/* Footer */}
        <div className="p-3 border-t border-border">
           {/* Performance Metrics */}
           {!isCollapsed && (
             <div className="mb-3 space-y-2">
               <div className="flex items-center justify-between text-xs">
                 <span className="text-muted-foreground">Facts</span>
                 <span className="font-medium">{(kbMetrics?.factCount || 0).toLocaleString()}</span>
               </div>
               <Progress value={Math.min((kbMetrics?.factCount || 0) / 10, 100)} className="h-1" />
               
               <div className="flex items-center justify-between text-xs">
                 <span className="text-muted-foreground">Learning</span>
                 <span className="font-medium">{kbMetrics?.growthRate?.toFixed(1) || '0.0'}/min</span>
               </div>
               <Progress value={Math.min((kbMetrics?.growthRate || 0) * 10, 100)} className="h-1" />
             </div>
           )}
           
           {/* Collapse Toggle */}
           <Button
             variant="ghost"
             size="sm"
             onClick={() => setIsCollapsed(!isCollapsed)}
             className={cn(
               "w-full",
               isCollapsed && "p-2"
             )}
           >
             {isCollapsed ? (
               <ChevronRight className="w-4 h-4" />
             ) : (
               <>
                 <ChevronLeft className="w-4 h-4 mr-2" />
                 Collapse
               </>
             )}
           </Button>
         </div>
       </motion.nav>
     </TooltipProvider>
   );
 };

 export default ProNavigation;
