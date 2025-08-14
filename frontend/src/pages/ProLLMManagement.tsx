import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from '@/components/ui/dialog';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useGovernorStore } from '@/stores/useGovernorStore';
import wsService from '@/services/websocket';
import {
  Bot,
  Plus,
  Settings,
  Trash2,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Network,
  Key,
  Eye,
  EyeOff,
  Loader2,
  Info,
  Server,
  Cpu
} from 'lucide-react';
import { cn } from '@/lib/utils';

// Provider templates for easy setup
const PROVIDER_TEMPLATES = {
  openai: {
    name: 'OpenAI',
    baseUrl: 'https://api.openai.com/v1',
    models: ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo'],
    requiresApiKey: true,
    icon: '🤖'
  },
  anthropic: {
    name: 'Anthropic',
    baseUrl: 'https://api.anthropic.com/v1',
    models: ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku'],
    requiresApiKey: true,
    icon: '🧠'
  },
  deepseek: {
    name: 'DeepSeek',
    baseUrl: 'https://api.deepseek.com',
    models: ['deepseek-chat', 'deepseek-coder'],
    requiresApiKey: true,
    icon: '🔍'
  },
  mistral: {
    name: 'Mistral',
    baseUrl: 'https://api.mistral.ai/v1',
    models: ['mistral-large-latest', 'mistral-medium'],
    requiresApiKey: true,
    icon: '🌊'
  },
  local: {
    name: 'Local LLM (Ollama)',
    baseUrl: 'http://localhost:11434',
    models: ['llama2', 'mistral', 'codellama'],
    requiresApiKey: false,
    icon: '💻'
  },
  custom: {
    name: 'Custom Provider',
    baseUrl: '',
    models: [],
    requiresApiKey: true,
    icon: '⚙️'
  }
};

const ProLLMManagement: React.FC = () => {
  const isConnected = useGovernorStore(state => state.isConnected);
  const llmProviders = useGovernorStore(state => state.llmProviders);
  
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [showApiKey, setShowApiKey] = useState<Record<string, boolean>>({});
  const [testingConnection, setTestingConnection] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    type: 'openai',
    name: '',
    baseUrl: '',
    apiKey: '',
    model: ''
  });

  const handleAddProvider = async () => {
    const template = PROVIDER_TEMPLATES[formData.type as keyof typeof PROVIDER_TEMPLATES];
    
    // Send to backend
    wsService.emit('add_llm_provider', {
      name: formData.name || template.name,
      type: formData.type,
      baseUrl: formData.baseUrl || template.baseUrl,
      apiKey: formData.apiKey,
      model: formData.model
    });

    setShowAddDialog(false);
    resetForm();
  };

  const handleRemoveProvider = (providerName: string) => {
    if (confirm(`Are you sure you want to remove ${providerName}?`)) {
      wsService.emit('remove_llm_provider', { name: providerName });
    }
  };

  const handleTestConnection = async (providerName: string) => {
    setTestingConnection(providerName);
    wsService.emit('test_llm_connection', { name: providerName });
    
    // Reset after timeout
    setTimeout(() => {
      setTestingConnection(null);
    }, 5000);
  };

  const resetForm = () => {
    setFormData({
      type: 'openai',
      name: '',
      baseUrl: '',
      apiKey: '',
      model: ''
    });
  };

  const handleProviderTypeChange = (type: string) => {
    const template = PROVIDER_TEMPLATES[type as keyof typeof PROVIDER_TEMPLATES];
    setFormData({
      ...formData,
      type,
      name: template.name,
      baseUrl: template.baseUrl,
      model: template.models?.[0] || ''
    });
  };

  if (!isConnected) {
    return (
      <div className="h-full p-6 flex items-center justify-center">
        <Card className="max-w-md">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-yellow-500" />
              Not Connected
            </CardTitle>
            <CardDescription>
              Connect to the backend to manage LLM providers
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={() => window.location.reload()} className="w-full">
              Retry Connection
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="h-full p-6 space-y-6 overflow-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">LLM Provider Management</h1>
          <p className="text-muted-foreground mt-1">
            Configure AI language model providers for knowledge generation
          </p>
        </div>
        <Dialog open={showAddDialog} onOpenChange={setShowAddDialog}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Add Provider
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[500px]">
            <DialogHeader>
              <DialogTitle>Add LLM Provider</DialogTitle>
              <DialogDescription>
                Configure a new language model provider
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label>Provider Type</Label>
                <Select
                  value={formData.type}
                  onValueChange={handleProviderTypeChange}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.entries(PROVIDER_TEMPLATES).map(([key, template]) => (
                      <SelectItem key={key} value={key}>
                        <span className="flex items-center gap-2">
                          <span>{template.icon}</span>
                          {template.name}
                        </span>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Provider Name</Label>
                <Input
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g., My OpenAI Instance"
                />
              </div>

              <div className="space-y-2">
                <Label>Base URL</Label>
                <Input
                  value={formData.baseUrl}
                  onChange={(e) => setFormData({ ...formData, baseUrl: e.target.value })}
                  placeholder="https://api.openai.com/v1"
                />
              </div>

              {PROVIDER_TEMPLATES[formData.type as keyof typeof PROVIDER_TEMPLATES]?.requiresApiKey && (
                <div className="space-y-2">
                  <Label>API Key</Label>
                  <Input
                    type="password"
                    value={formData.apiKey}
                    onChange={(e) => setFormData({ ...formData, apiKey: e.target.value })}
                    placeholder="sk-..."
                  />
                </div>
              )}

              <div className="space-y-2">
                <Label>Model</Label>
                {PROVIDER_TEMPLATES[formData.type as keyof typeof PROVIDER_TEMPLATES]?.models.length > 0 ? (
                  <Select
                    value={formData.model}
                    onValueChange={(value) => setFormData({ ...formData, model: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {PROVIDER_TEMPLATES[formData.type as keyof typeof PROVIDER_TEMPLATES].models.map(model => (
                        <SelectItem key={model} value={model}>
                          {model}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                ) : (
                  <Input
                    value={formData.model}
                    onChange={(e) => setFormData({ ...formData, model: e.target.value })}
                    placeholder="Enter model name"
                  />
                )}
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setShowAddDialog(false)}>
                Cancel
              </Button>
              <Button onClick={handleAddProvider}>
                Add Provider
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Current Providers */}
      <div className="space-y-4">
        <h2 className="text-lg font-semibold">Configured Providers</h2>
        
        {llmProviders && llmProviders.length > 0 ? (
          <div className="grid gap-4">
            {llmProviders.map((provider) => (
              <Card key={provider.name}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="text-2xl">
                        {provider.name.toLowerCase().includes('deepseek') ? '🔍' :
                         provider.name.toLowerCase().includes('mistral') ? '🌊' :
                         provider.name.toLowerCase().includes('gemini') ? '💎' :
                         provider.name.toLowerCase().includes('openai') ? '🤖' :
                         provider.name.toLowerCase().includes('anthropic') ? '🧠' : '🤖'}
                      </div>
                      <div>
                        <CardTitle className="text-lg">{provider.name}</CardTitle>
                        <CardDescription>{provider.model || 'Default model'}</CardDescription>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant={provider.status === 'connected' ? 'default' : 'secondary'}>
                        {provider.status === 'connected' ? (
                          <CheckCircle2 className="w-3 h-3 mr-1" />
                        ) : (
                          <XCircle className="w-3 h-3 mr-1" />
                        )}
                        {provider.status || 'unknown'}
                      </Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {/* Provider Details */}
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground">Type</p>
                        <p className="font-medium">{provider.type || 'API'}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Status</p>
                        <p className="font-medium">{provider.status || 'Unknown'}</p>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center justify-end gap-2 pt-3 border-t">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleTestConnection(provider.name)}
                        disabled={testingConnection === provider.name}
                      >
                        {testingConnection === provider.name ? (
                          <>
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                            Testing...
                          </>
                        ) : (
                          <>
                            <Network className="w-4 h-4 mr-2" />
                            Test Connection
                          </>
                        )}
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleRemoveProvider(provider.name)}
                        className="text-red-500 hover:text-red-600"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <Card className="p-8">
            <div className="text-center">
              <Bot className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">No Providers Configured</h3>
              <p className="text-muted-foreground mb-4">
                Add your first LLM provider to enable knowledge generation
              </p>
              <Button onClick={() => setShowAddDialog(true)}>
                <Plus className="w-4 h-4 mr-2" />
                Add Provider
              </Button>
            </div>
          </Card>
        )}
      </div>

      {/* Provider Information */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Info className="w-5 h-5" />
            Provider Information
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              LLM providers are used by the learning engines (Aethelred and Thesis) to generate new knowledge. 
              Each provider can have different capabilities and costs.
            </AlertDescription>
          </Alert>

          <div className="space-y-3">
            <div>
              <h4 className="font-medium mb-2">Current System Providers:</h4>
              <ul className="space-y-1 text-sm text-muted-foreground">
                <li>• <strong>DeepSeek:</strong> Primary provider for exploration (Aethelred engine)</li>
                <li>• <strong>Mistral:</strong> Used for logical proofs and validation</li>
                <li>• <strong>Gemini:</strong> Hypothesis generation (Thesis engine)</li>
              </ul>
            </div>

            <div>
              <h4 className="font-medium mb-2">Adding Custom Providers:</h4>
              <ul className="space-y-1 text-sm text-muted-foreground">
                <li>• Ensure your API key has sufficient credits</li>
                <li>• Test the connection before enabling auto-learning</li>
                <li>• Monitor usage to control costs</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="w-5 h-5" />
            Provider Settings
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <Label>Request Timeout</Label>
                <p className="text-sm text-muted-foreground">
                  Maximum time to wait for provider response
                </p>
              </div>
              <Select defaultValue="60">
                <SelectTrigger className="w-[100px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="30">30s</SelectItem>
                  <SelectItem value="60">60s</SelectItem>
                  <SelectItem value="120">120s</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <Label>Retry Failed Requests</Label>
                <p className="text-sm text-muted-foreground">
                  Number of retries for failed API calls
                </p>
              </div>
              <Select defaultValue="3">
                <SelectTrigger className="w-[100px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="0">None</SelectItem>
                  <SelectItem value="1">1 retry</SelectItem>
                  <SelectItem value="3">3 retries</SelectItem>
                  <SelectItem value="5">5 retries</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <Label>Load Balancing Strategy</Label>
                <p className="text-sm text-muted-foreground">
                  How to distribute requests across providers
                </p>
              </div>
              <Select defaultValue="intent">
                <SelectTrigger className="w-[150px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="intent">Intent-based</SelectItem>
                  <SelectItem value="round-robin">Round Robin</SelectItem>
                  <SelectItem value="fallback">Fallback Chain</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ProLLMManagement;
