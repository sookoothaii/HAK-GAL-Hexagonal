import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Bot,
  Settings2,
  Zap,
  Timer,
  Eye,
  EyeOff,
  TestTube,
  Save,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Loader2,
  RefreshCw,
  Info,
  Key,
  Link,
  Rocket,
  Cloud,
  Server
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface LLMProvider {
  id: string;
  name: string;
  icon: any;
  color: string;
  description: string;
  apiKeyEnvVar: string;
  docUrl: string;
  enabled: boolean;
  order: number;
  hasEnvKey?: boolean;
  tempApiKey?: string;
  responseTime?: number;
  lastTested?: string;
}

const PROVIDER_CONFIG: Record<string, Omit<LLMProvider, 'enabled' | 'order'>> = {
  groq: {
    id: 'groq',
    name: 'Groq',
    icon: Rocket,
    color: 'text-orange-500',
    description: 'Lightning-fast inference with LPU technology (~1.5s)',
    apiKeyEnvVar: 'GROQ_API_KEY',
    docUrl: 'https://console.groq.com/keys'
  },
  deepseek: {
    id: 'deepseek',
    name: 'DeepSeek',
    icon: Zap,
    color: 'text-blue-500',
    description: 'High-quality responses with competitive pricing (~3s)',
    apiKeyEnvVar: 'DEEPSEEK_API_KEY',
    docUrl: 'https://platform.deepseek.com/'
  },
  gemini: {
    id: 'gemini',
    name: 'Google Gemini',
    icon: Cloud,
    color: 'text-purple-500',
    description: 'Google\'s AI with generous free tier (~5s)',
    apiKeyEnvVar: 'GOOGLE_API_KEY',
    docUrl: 'https://makersuite.google.com/app/apikey'
  },
  claude: {
    id: 'claude',
    name: 'Anthropic Claude',
    icon: Bot,
    color: 'text-green-500',
    description: 'Advanced reasoning and safety features (~8s)',
    apiKeyEnvVar: 'ANTHROPIC_API_KEY',
    docUrl: 'https://console.anthropic.com/'
  },
  ollama: {
    id: 'ollama',
    name: 'Ollama (Local)',
    icon: Server,
    color: 'text-gray-500',
    description: 'Local LLM, no API key needed (~10s)',
    apiKeyEnvVar: '',
    docUrl: 'https://ollama.ai/'
  }
};

interface LLMConfigurationProps {
  onConfigChange?: (config: any) => void;
}

export const LLMConfiguration: React.FC<LLMConfigurationProps> = ({ onConfigChange }) => {
  const [providers, setProviders] = useState<LLMProvider[]>([]);
  const [showApiKeys, setShowApiKeys] = useState<Record<string, boolean>>({});
  const [testing, setTesting] = useState<Record<string, boolean>>({});
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);

  // Load configuration on mount
  useEffect(() => {
    loadConfiguration();
    checkEnvironmentKeys();
  }, []);

  const loadConfiguration = async () => {
    try {
      const { API_BASE_URL } = await import('@/config/backends');
      const response = await fetch(`${API_BASE_URL}/api/llm/config`);
      if (response.ok) {
        const data = await response.json();
        
        // Merge with default config
        const mergedProviders = Object.entries(PROVIDER_CONFIG).map(([id, config]) => {
          const savedProvider = data.providers?.[id] || {};
          const enabledList = data.enabled_providers || [];
          const orderList = data.provider_order || [];
          
          return {
            ...config,
            enabled: enabledList.includes(id),
            order: orderList.indexOf(id) !== -1 ? orderList.indexOf(id) : 999,
            tempApiKey: data.api_keys?.[id] || '',
            ...savedProvider
          };
        }).sort((a, b) => a.order - b.order);
        
        setProviders(mergedProviders);
      }
    } catch (error) {
      console.error('Failed to load LLM configuration:', error);
      // Use default configuration
      const defaultProviders = Object.values(PROVIDER_CONFIG).map((config, index) => ({
        ...config,
        enabled: true,
        order: index
      }));
      setProviders(defaultProviders);
    } finally {
      setLoading(false);
    }
  };

  const checkEnvironmentKeys = async () => {
    try {
      const { API_BASE_URL } = await import('@/config/backends');
      const response = await fetch(`${API_BASE_URL}/api/llm/check-env-keys`);
      if (response.ok) {
        const envKeys = await response.json();
        setProviders(prev => prev.map(p => ({
          ...p,
          hasEnvKey: envKeys[p.id] || false
        })));
      }
    } catch (error) {
      console.error('Failed to check environment keys:', error);
    }
  };

  const handleToggleProvider = (providerId: string) => {
    setProviders(prev => prev.map(p => 
      p.id === providerId ? { ...p, enabled: !p.enabled } : p
    ));
  };

  const handleApiKeyChange = (providerId: string, value: string) => {
    setProviders(prev => prev.map(p => 
      p.id === providerId ? { ...p, tempApiKey: value } : p
    ));
  };

  const [draggedIndex, setDraggedIndex] = useState<number | null>(null);
  const [dragOverIndex, setDragOverIndex] = useState<number | null>(null);

  const handleDragStart = (e: React.DragEvent, index: number) => {
    setDraggedIndex(index);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e: React.DragEvent, index: number) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    setDragOverIndex(index);
  };

  const handleDragEnd = () => {
    setDraggedIndex(null);
    setDragOverIndex(null);
  };

  const handleDrop = (e: React.DragEvent, dropIndex: number) => {
    e.preventDefault();
    
    if (draggedIndex === null || draggedIndex === dropIndex) {
      return;
    }

    const enabledProviders = providers
      .filter(p => p.enabled)
      .sort((a, b) => a.order - b.order);
    
    const draggedProvider = enabledProviders[draggedIndex];
    const newProviders = [...enabledProviders];
    
    // Remove dragged item
    newProviders.splice(draggedIndex, 1);
    
    // Insert at new position
    newProviders.splice(dropIndex, 0, draggedProvider);
    
    // Update order for all providers
    const updatedProviders = providers.map(provider => {
      const enabledIndex = newProviders.findIndex(p => p.id === provider.id);
      if (enabledIndex !== -1) {
        return { ...provider, order: enabledIndex };
      }
      return provider;
    });
    
    setProviders(updatedProviders);
    setDraggedIndex(null);
    setDragOverIndex(null);
  };

  const handleTestProvider = async (providerId: string) => {
    setTesting(prev => ({ ...prev, [providerId]: true }));
    
    try {
      const provider = providers.find(p => p.id === providerId);
      const { API_BASE_URL } = await import('@/config/backends');
      const response = await fetch(`${API_BASE_URL}/api/llm/test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provider: providerId,
          apiKey: provider?.tempApiKey || undefined
        })
      });
      
      const result = await response.json();
      
      setProviders(prev => prev.map(p => 
        p.id === providerId 
          ? { 
              ...p, 
              responseTime: result.response_time,
              lastTested: new Date().toISOString()
            } 
          : p
      ));
      
      if (!result.success) {
        alert(result.error || 'Test failed');
      }
    } catch (error) {
      console.error('Test failed:', error);
      alert('Failed to test provider');
    } finally {
      setTesting(prev => ({ ...prev, [providerId]: false }));
    }
  };

  const handleSaveConfiguration = async () => {
    setSaving(true);
    
    try {
      const config = {
        providers: providers.map(p => ({
          id: p.id,
          enabled: p.enabled,
          order: p.order,
          tempApiKey: p.tempApiKey
        }))
      };
      
      const { API_BASE_URL } = await import('@/config/backends');
      const response = await fetch(`${API_BASE_URL}/api/llm/config`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      });
      
      if (response.ok) {
        // Notify parent component
        onConfigChange?.(config);
        alert('Configuration saved successfully');
      } else {
        alert('Failed to save configuration');
      }
    } catch (error) {
      console.error('Save failed:', error);
      alert('Failed to save configuration');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center p-6">
          <Loader2 className="h-6 w-6 animate-spin" />
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bot className="w-5 h-5" />
            LLM Provider Configuration
          </CardTitle>
          <CardDescription>
            Configure which LLM providers to use and in what order
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Alert className="mb-4">
            <Info className="h-4 w-4" />
            <AlertDescription>
              Providers are tried in order from top to bottom. Disable slow providers to improve response times.
              <br />
              <strong>Performance tip:</strong> Groq offers ~97.5% faster responses than traditional providers!
            </AlertDescription>
          </Alert>

          <Tabs defaultValue="providers" className="space-y-4">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="providers">Providers</TabsTrigger>
              <TabsTrigger value="chain">Chain Order</TabsTrigger>
            </TabsList>

            <TabsContent value="providers" className="space-y-4">
              {providers.map((provider) => {
                const Icon = provider.icon;
                return (
                  <Card key={provider.id} className={cn("border", !provider.enabled && "opacity-60")}>
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <Icon className={cn("w-5 h-5", provider.color)} />
                          <div>
                            <CardTitle className="text-base">{provider.name}</CardTitle>
                            <CardDescription className="text-sm">
                              {provider.description}
                            </CardDescription>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          {provider.responseTime && (
                            <Badge variant="secondary" className="text-xs">
                              <Timer className="w-3 h-3 mr-1" />
                              {provider.responseTime}ms
                            </Badge>
                          )}
                          <Switch
                            checked={provider.enabled}
                            onCheckedChange={() => handleToggleProvider(provider.id)}
                          />
                        </div>
                      </div>
                    </CardHeader>
                    {provider.enabled && (
                      <CardContent className="space-y-3">
                        <div className="flex items-center gap-2">
                          {provider.hasEnvKey ? (
                            <Badge variant="default" className="text-xs">
                              <Key className="w-3 h-3 mr-1" />
                              Environment Key Set
                            </Badge>
                          ) : provider.apiKeyEnvVar ? (
                            <Badge variant="outline" className="text-xs">
                              <AlertTriangle className="w-3 h-3 mr-1" />
                              No Environment Key
                            </Badge>
                          ) : (
                            <Badge variant="secondary" className="text-xs">
                              <Server className="w-3 h-3 mr-1" />
                              Local Provider
                            </Badge>
                          )}
                          {provider.docUrl && (
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => window.open(provider.docUrl, '_blank')}
                            >
                              <Link className="w-3 h-3 mr-1" />
                              Get API Key
                            </Button>
                          )}
                        </div>

                        {provider.apiKeyEnvVar && (
                          <div className="space-y-2">
                            <Label className="text-sm">
                              Temporary API Key (overrides {provider.apiKeyEnvVar})
                            </Label>
                            <div className="flex gap-2">
                              <div className="relative flex-1">
                                <Input
                                  type={showApiKeys[provider.id] ? "text" : "password"}
                                  value={provider.tempApiKey || ''}
                                  onChange={(e) => handleApiKeyChange(provider.id, e.target.value)}
                                  placeholder={`Enter ${provider.name} API key (optional)`}
                                />
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  className="absolute right-1 top-1/2 -translate-y-1/2 h-7 w-7 p-0"
                                  onClick={() => setShowApiKeys(prev => ({ 
                                    ...prev, 
                                    [provider.id]: !prev[provider.id] 
                                  }))}
                                >
                                  {showApiKeys[provider.id] ? 
                                    <EyeOff className="h-4 w-4" /> : 
                                    <Eye className="h-4 w-4" />
                                  }
                                </Button>
                              </div>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleTestProvider(provider.id)}
                                disabled={testing[provider.id]}
                              >
                                {testing[provider.id] ? (
                                  <Loader2 className="h-4 w-4 animate-spin" />
                                ) : (
                                  <>
                                    <TestTube className="h-4 w-4 mr-1" />
                                    Test
                                  </>
                                )}
                              </Button>
                            </div>
                          </div>
                        )}
                      </CardContent>
                    )}
                  </Card>
                );
              })}
            </TabsContent>

            <TabsContent value="chain" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Provider Chain Order</CardTitle>
                  <CardDescription>
                    Drag and drop to reorder providers. Only enabled providers will be used.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {providers
                      .filter(p => p.enabled)
                      .sort((a, b) => a.order - b.order)
                      .map((provider, index) => {
                        const Icon = provider.icon;
                        return (
                          <div
                            key={provider.id}
                            draggable
                            onDragStart={(e) => handleDragStart(e, index)}
                            onDragOver={(e) => handleDragOver(e, index)}
                            onDragEnd={handleDragEnd}
                            onDrop={(e) => handleDrop(e, index)}
                            className={cn(
                              "flex items-center gap-3 p-3 border rounded-lg bg-muted/50 cursor-move transition-all",
                              draggedIndex === index && "opacity-50",
                              dragOverIndex === index && "border-primary bg-primary/10"
                            )}
                          >
                            <div className="text-muted-foreground font-mono text-sm select-none">
                              ⋮⋮ {index + 1}
                            </div>
                            <Icon className={cn("w-4 h-4", provider.color)} />
                            <span className="font-medium">{provider.name}</span>
                            {provider.responseTime && (
                              <Badge variant="secondary" className="ml-auto text-xs">
                                {provider.responseTime}ms
                              </Badge>
                            )}
                          </div>
                        );
                      })}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>

          <div className="flex justify-end gap-2 mt-4">
            <Button variant="outline" onClick={() => loadConfiguration()}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Reset
            </Button>
            <Button onClick={handleSaveConfiguration} disabled={saving}>
              {saving ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Save className="h-4 w-4 mr-2" />
              )}
              Save Configuration
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default LLMConfiguration;
