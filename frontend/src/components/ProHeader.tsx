import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useGovernorStore } from '@/stores/useGovernorStore';
import { motion } from 'framer-motion';
import {
  Search,
  Bell,
  Settings,
  User,
  LogOut,
  Moon,
  Sun,
  Menu,
  X,
  Command,
  Sparkles,
  Zap,
  Download,
  Upload,
  RefreshCw,
  Globe,
  Shield,
  Activity,
  Server
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  DropdownMenuShortcut,
} from '@/components/ui/dropdown-menu';
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
  CommandShortcut,
} from '@/components/ui/command';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { useTheme } from '@/components/theme-provider';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';
import { useGovernorSocket } from '@/hooks/useGovernorSocket';

interface ProHeaderProps {
  onNavToggle?: () => void;
}

const ProHeader: React.FC<ProHeaderProps> = ({ onNavToggle }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { theme, setTheme } = useTheme();
  const [commandOpen, setCommandOpen] = useState(false);
  const [notifications, setNotifications] = useState([
    { id: 1, title: 'System Update', message: 'HAK-GAL v2.0 is now available', time: '5m ago', unread: true },
    { id: 2, title: 'Knowledge Milestone', message: 'Reached 100k facts!', time: '1h ago', unread: true },
    { id: 3, title: 'Governor Alert', message: 'Strategy optimization complete', time: '2h ago', unread: false },
  ]);
  
  const wsService = useGovernorSocket();
  
  // Store data
  const isConnected = useGovernorStore(state => state.isConnected);
  const systemStatus = useGovernorStore(state => state.systemStatus);
  const governorRunning = useGovernorStore(state => state.governor.running);
  const kbMetrics = useGovernorStore(state => state.kb.metrics);
  
  // Breadcrumb generation
  const breadcrumbs = location.pathname.split('/').filter(Boolean).map((segment, index, array) => {
    const path = '/' + array.slice(0, index + 1).join('/');
    const label = segment.charAt(0).toUpperCase() + segment.slice(1).replace(/-/g, ' ');
    return { path, label };
  });
  
  // Command palette items
  const commandItems = [
    { group: 'Navigation', items: [
      { label: 'Dashboard', icon: <Activity className="w-4 h-4" />, shortcut: 'D', action: () => navigate('/dashboard') },
      { label: 'Knowledge Base', icon: <Globe className="w-4 h-4" />, shortcut: 'K', action: () => navigate('/knowledge') },
      { label: 'Governor Control', icon: <Shield className="w-4 h-4" />, shortcut: 'G', action: () => navigate('/governor') },
    ]},
    { group: 'Actions', items: [
      { label: 'Export Data', icon: <Download className="w-4 h-4" />, action: () => toast.success('Export started') },
      { label: 'Import Data', icon: <Upload className="w-4 h-4" />, action: () => toast.info('Import dialog opened') },
      { label: 'Refresh All', icon: <RefreshCw className="w-4 h-4" />, shortcut: 'R', action: () => window.location.reload() },
    ]},
  ];
  
  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.metaKey || e.ctrlKey) {
        switch (e.key) {
          case 'k':
            e.preventDefault();
            setCommandOpen(true);
            break;
          case 'd':
            e.preventDefault();
            navigate('/dashboard');
            break;
          case 'g':
            e.preventDefault();
            navigate('/governor');
            break;
        }
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [navigate]);
  
  const unreadCount = notifications.filter(n => n.unread).length;
  
  return (
    <>
      <header className="h-16 bg-card border-b border-border flex items-center justify-between px-6 relative z-50">
        {/* Left Section */}
        <div className="flex items-center gap-4">
          {/* Menu Toggle */}
          <Button
            variant="ghost"
            size="icon"
            onClick={onNavToggle}
            className="lg:hidden"
          >
            <Menu className="h-5 w-5" />
          </Button>
          
          {/* Breadcrumbs */}
          <nav className="flex items-center gap-2 text-sm">
            <a href="/" className="text-muted-foreground hover:text-foreground transition-colors">
              Home
            </a>
            {breadcrumbs.map((crumb, index) => (
              <React.Fragment key={crumb.path}>
                <span className="text-muted-foreground">/</span>
                <a
                  href={crumb.path}
                  className={cn(
                    "transition-colors",
                    index === breadcrumbs.length - 1
                      ? "text-foreground font-medium"
                      : "text-muted-foreground hover:text-foreground"
                  )}
                >
                  {crumb.label}
                </a>
              </React.Fragment>
            ))}
          </nav>
        </div>
        
        {/* Center Section - Search */}
        <div className="flex-1 max-w-xl mx-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
            <Input
              type="search"
              placeholder="Search knowledge base... (⌘K)"
              className="w-full pl-10 pr-4 bg-muted/50 border-muted focus:bg-background"
              onFocus={() => setCommandOpen(true)}
            />
            <kbd className="absolute right-3 top-1/2 transform -translate-y-1/2 pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground opacity-100">
              <span className="text-xs">⌘</span>K
            </kbd>
          </div>
        </div>
        
        {/* Right Section */}
        <div className="flex items-center gap-3">
          {/* Backend Status Badge - No switching, just display */}
          <Badge variant="outline" className="hidden lg:flex items-center gap-1 text-xs">
            <Server className="w-3 h-3" />
            Port 5002 (WRITE)
          </Badge>

          {/* Governor Control Button */}
          <Button
            onClick={() => wsService.toggleGovernor(!governorRunning)}
            variant={governorRunning ? "destructive" : "default"}
            size="sm"
            disabled={!isConnected}
            className="flex items-center gap-2"
          >
            <Zap className="w-4 h-4" />
            {governorRunning ? 'Stop' : 'Start'} Governor
          </Button>

          {/* Live Status Indicators */}
          <div className="hidden lg:flex items-center gap-4 mr-4">
            <div className="flex items-center gap-2">
              <div className={cn(
                "w-2 h-2 rounded-full",
                isConnected ? "bg-green-500" : "bg-red-500"
              )} />
              <span className="text-xs text-muted-foreground">
                WebSocket
              </span>
            </div>
            
            {governorRunning && (
              <Badge variant="outline" className="text-xs">
                <Zap className="w-3 h-3 mr-1" />
                Governor Active
              </Badge>
            )}
            
            <Badge variant="secondary" className="text-xs font-mono">
              {(kbMetrics?.factCount || kbMetrics?.fact_count || 0).toLocaleString()} facts
            </Badge>
          </div>
          
          {/* Theme Toggle */}
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          >
            {theme === 'dark' ? (
              <Sun className="h-5 w-5" />
            ) : (
              <Moon className="h-5 w-5" />
            )}
          </Button>
          
          {/* Notifications */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="relative">
                <Bell className="h-5 w-5" />
                {unreadCount > 0 && (
                  <span className="absolute -top-1 -right-1 h-5 w-5 rounded-full bg-destructive text-xs text-destructive-foreground flex items-center justify-center">
                    {unreadCount}
                  </span>
                )}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-80">
              <DropdownMenuLabel className="flex items-center justify-between">
                Notifications
                <Button variant="ghost" size="sm" className="h-auto p-0 text-xs">
                  Mark all read
                </Button>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              {notifications.map(notification => (
                <DropdownMenuItem
                  key={notification.id}
                  className="flex flex-col items-start p-3 cursor-pointer"
                >
                  <div className="flex items-center justify-between w-full">
                    <span className="font-medium">{notification.title}</span>
                    {notification.unread && (
                      <div className="w-2 h-2 rounded-full bg-primary" />
                    )}
                  </div>
                  <span className="text-sm text-muted-foreground">{notification.message}</span>
                  <span className="text-xs text-muted-foreground mt-1">{notification.time}</span>
                </DropdownMenuItem>
              ))}
              <DropdownMenuSeparator />
              <DropdownMenuItem className="text-center cursor-pointer">
                View all notifications
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
          
          {/* User Menu */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                <Avatar className="h-8 w-8">
                  <AvatarImage src="/avatar.png" alt="User" />
                  <AvatarFallback>AI</AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-56" align="end" forceMount>
              <DropdownMenuLabel className="font-normal">
                <div className="flex flex-col space-y-1">
                  <p className="text-sm font-medium leading-none">AI Operator</p>
                  <p className="text-xs leading-none text-muted-foreground">
                    operator@hak-gal.ai
                  </p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem>
                <User className="mr-2 h-4 w-4" />
                <span>Profile</span>
                <DropdownMenuShortcut>⇧⌘P</DropdownMenuShortcut>
              </DropdownMenuItem>
              <DropdownMenuItem>
                <Settings className="mr-2 h-4 w-4" />
                <span>Settings</span>
                <DropdownMenuShortcut>⌘S</DropdownMenuShortcut>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem className="text-destructive">
                <LogOut className="mr-2 h-4 w-4" />
                <span>Log out</span>
                <DropdownMenuShortcut>⇧⌘Q</DropdownMenuShortcut>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </header>
      
      {/* Command Palette */}
      <CommandDialog open={commandOpen} onOpenChange={setCommandOpen}>
        <CommandInput placeholder="Type a command or search..." />
        <CommandList>
          <CommandEmpty>No results found.</CommandEmpty>
          {commandItems.map(group => (
            <React.Fragment key={group.group}>
              <CommandGroup heading={group.group}>
                {group.items.map(item => (
                  <CommandItem
                    key={item.label}
                    onSelect={() => {
                      item.action();
                      setCommandOpen(false);
                    }}
                  >
                    {item.icon}
                    <span className="ml-2">{item.label}</span>
                    {item.shortcut && (
                      <CommandShortcut>⌘{item.shortcut}</CommandShortcut>
                    )}
                  </CommandItem>
                ))}
              </CommandGroup>
              <CommandSeparator />
            </React.Fragment>
          ))}
        </CommandList>
      </CommandDialog>
    </>
  );
};

export default ProHeader;