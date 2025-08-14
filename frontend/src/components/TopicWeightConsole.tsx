import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Slider } from '@/components/ui/slider';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useGovernorStore } from '@/stores/useGovernorStore';
import wsService from '@/services/websocket';
import {
  Focus,
  Brain,
  Sparkles,
  Target,
  Plus,
  Minus,
  RefreshCw,
  Save,
  Shuffle,
  TrendingUp,
  BarChart,
  Info,
  AlertTriangle,
  CheckCircle2,
  Search,
  Hash,
  Star,
  Zap,
  Globe,
  Book,
  Atom,
  Code,
  Heart,
  Lightbulb,
  Rocket
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface TopicWeight {
  name: string;
  weight: number;
  category: string;
  icon: any;
  color: string;
}

const TOPIC_CATEGORIES = {
  science: {
    name: 'Science',
    icon: Atom,
    color: 'text-blue-500',
    bgColor: 'bg-blue-500/10',
    topics: [
      'Physics', 'Chemistry', 'Biology', 'Astronomy', 'Mathematics',
      'Quantum Mechanics', 'Genetics', 'Neuroscience', 'Climate Science'
    ]
  },
  technology: {
    name: 'Technology',
    icon: Code,
    color: 'text-green-500',
    bgColor: 'bg-green-500/10',
    topics: [
      'Artificial Intelligence', 'Machine Learning', 'Blockchain', 'Cybersecurity',
      'Robotics', 'Internet of Things', 'Cloud Computing', 'Data Science'
    ]
  },
  philosophy: {
    name: 'Philosophy',
    icon: Lightbulb,
    color: 'text-purple-500',
    bgColor: 'bg-purple-500/10',
    topics: [
      'Ethics', 'Metaphysics', 'Epistemology', 'Logic', 'Aesthetics',
      'Political Philosophy', 'Philosophy of Mind', 'Existentialism'
    ]
  },
  general: {
    name: 'General Knowledge',
    icon: Book,
    color: 'text-orange-500',
    bgColor: 'bg-orange-500/10',
    topics: [
      'History', 'Geography', 'Literature', 'Art', 'Music',
      'Economics', 'Psychology', 'Sociology', 'Anthropology'
    ]
  }
};

const PRESET_DISTRIBUTIONS = {
  balanced: {
    name: 'Balanced',
    description: 'Equal weight across all topics',
    icon: Brain,
    distribution: 'uniform'
  },
  scientific: {
    name: 'Scientific Focus',
    description: 'Emphasize STEM topics',
    icon: Atom,
    distribution: { science: 60, technology: 25, philosophy: 10, general: 5 }
  },
  philosophical: {
    name: 'Philosophical',
    description: 'Deep theoretical exploration',
    icon: Lightbulb,
    distribution: { science: 20, technology: 15, philosophy: 50, general: 15 }
  },
  practical: {
    name: 'Practical',
    description: 'Real-world applications',
    icon: Rocket,
    distribution: { science: 25, technology: 45, philosophy: 10, general: 20 }
  }
};

const TopicWeightConsole: React.FC = () => {
  const [autoMode, setAutoMode] = useState(true);
  const [selectedPreset, setSelectedPreset] = useState('balanced');
  const [customTopics, setCustomTopics] = useState<TopicWeight[]>([]);
  const [newTopicName, setNewTopicName] = useState('');
  const [categoryWeights, setCategoryWeights] = useState({
    science: 25,
    technology: 25,
    philosophy: 25,
    general: 25
  });
  const [saving, setSaving] = useState(false);

  const isConnected = useGovernorStore(state => state.isConnected);
  const kbMetrics = useGovernorStore(state => state.kbMetrics);

  // Initialize with some default custom topics
  useEffect(() => {
    const savedTopics = localStorage.getItem('customTopics');
    if (savedTopics) {
      setCustomTopics(JSON.parse(savedTopics));
    }
  }, []);

  const handleAddCustomTopic = () => {
    if (newTopicName.trim()) {
      const newTopic: TopicWeight = {
        name: newTopicName.trim(),
        weight: 50,
        category: 'custom',
        icon: Star,
        color: 'text-yellow-500'
      };
      const updatedTopics = [...customTopics, newTopic];
      setCustomTopics(updatedTopics);
      localStorage.setItem('customTopics', JSON.stringify(updatedTopics));
      setNewTopicName('');
    }
  };

  const handleRemoveCustomTopic = (index: number) => {
    const updatedTopics = customTopics.filter((_, i) => i !== index);
    setCustomTopics(updatedTopics);
    localStorage.setItem('customTopics', JSON.stringify(updatedTopics));
  };

  const handleCustomTopicWeightChange = (index: number, weight: number) => {
    const updatedTopics = [...customTopics];
    updatedTopics[index].weight = weight;
    setCustomTopics(updatedTopics);
  };

  const handlePresetChange = (preset: string) => {
    setSelectedPreset(preset);
    const presetConfig = PRESET_DISTRIBUTIONS[preset as keyof typeof PRESET_DISTRIBUTIONS];
    
    if (presetConfig.distribution === 'uniform') {
      setCategoryWeights({
        science: 25,
        technology: 25,
        philosophy: 25,
        general: 25
      });
    } else if (typeof presetConfig.distribution === 'object') {
      setCategoryWeights(presetConfig.distribution as any);
    }
  };

  const handleSaveConfiguration = async () => {
    setSaving(true);
    
    // Send configuration to backend
    wsService.emit('set_topic_preferences', {
      autoMode,
      categoryWeights: autoMode ? categoryWeights : null,
      customTopics: !autoMode ? customTopics.map(t => ({
        name: t.name,
        weight: t.weight
      })) : null
    });

    // Save to localStorage
    localStorage.setItem('topicPreferences', JSON.stringify({
      autoMode,
      categoryWeights,
      selectedPreset
    }));

    setTimeout(() => setSaving(false), 1000);
  };

  const handleRandomizeWeights = () => {
    if (autoMode) {
      const weights = {
        science: Math.floor(Math.random() * 40) + 10,
        technology: Math.floor(Math.random() * 40) + 10,
        philosophy: Math.floor(Math.random() * 40) + 10,
        general: Math.floor(Math.random() * 40) + 10
      };
      
      // Normalize to 100%
      const total = Object.values(weights).reduce((a, b) => a + b, 0);
      Object.keys(weights).forEach(key => {
        weights[key as keyof typeof weights] = Math.round((weights[key as keyof typeof weights] / total) * 100);
      });
      
      setCategoryWeights(weights);
      setSelectedPreset('');
    } else {
      // Randomize custom topic weights
      const updatedTopics = customTopics.map(topic => ({
        ...topic,
        weight: Math.floor(Math.random() * 80) + 20
      }));
      setCustomTopics(updatedTopics);
    }
  };

  const getTotalWeight = () => {
    if (autoMode) {
      return Object.values(categoryWeights).reduce((a, b) => a + b, 0);
    } else {
      return customTopics.reduce((sum, topic) => sum + topic.weight, 0) || 100;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Controls */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span className="flex items-center gap-2">
              <Focus className="w-5 h-5" />
              Topic Focus Control
            </span>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <Label htmlFor="auto-mode">Auto Mode</Label>
                <Switch
                  id="auto-mode"
                  checked={autoMode}
                  onCheckedChange={setAutoMode}
                />
              </div>
              <Badge variant="secondary">
                {autoMode ? 'Category-Based' : 'Custom Topics'}
              </Badge>
            </div>
          </CardTitle>
          <CardDescription>
            {autoMode 
              ? 'Set learning priorities by knowledge categories'
              : 'Define specific topics for targeted exploration'}
          </CardDescription>
        </CardHeader>
      </Card>

      <Tabs defaultValue={autoMode ? "categories" : "custom"} value={autoMode ? "categories" : "custom"}>
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="categories" disabled={!autoMode}>
            Category Weights
          </TabsTrigger>
          <TabsTrigger value="custom" disabled={autoMode}>
            Custom Topics
          </TabsTrigger>
        </TabsList>

        {/* Category-Based Mode */}
        <TabsContent value="categories" className="space-y-4">
          {/* Preset Selection */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Distribution Presets</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-3">
                {Object.entries(PRESET_DISTRIBUTIONS).map(([key, preset]) => {
                  const Icon = preset.icon;
                  const isSelected = selectedPreset === key;
                  return (
                    <Card
                      key={key}
                      className={cn(
                        "cursor-pointer transition-all hover:shadow-md",
                        isSelected && "ring-2 ring-primary"
                      )}
                      onClick={() => handlePresetChange(key)}
                    >
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm flex items-center gap-2">
                          <Icon className="w-4 h-4" />
                          {preset.name}
                          {isSelected && <CheckCircle2 className="w-4 h-4 ml-auto text-primary" />}
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <p className="text-xs text-muted-foreground">
                          {preset.description}
                        </p>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </CardContent>
          </Card>

          {/* Category Weight Sliders */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center justify-between">
                <span>Category Weights</span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleRandomizeWeights}
                >
                  <Shuffle className="w-4 h-4 mr-2" />
                  Randomize
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {Object.entries(TOPIC_CATEGORIES).map(([key, category]) => {
                const Icon = category.icon;
                const weight = categoryWeights[key as keyof typeof categoryWeights];
                return (
                  <div key={key} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className={cn("p-2 rounded-lg", category.bgColor)}>
                          <Icon className={cn("w-4 h-4", category.color)} />
                        </div>
                        <div>
                          <Label>{category.name}</Label>
                          <p className="text-xs text-muted-foreground">
                            {category.topics.slice(0, 3).join(', ')}...
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium w-12 text-right">
                          {weight}%
                        </span>
                        <Badge 
                          variant="secondary"
                          className={cn(
                            weight > 35 && "bg-green-500/20 text-green-700",
                            weight < 15 && "bg-red-500/20 text-red-700"
                          )}
                        >
                          {weight > 35 ? 'High' : weight < 15 ? 'Low' : 'Normal'}
                        </Badge>
                      </div>
                    </div>
                    <Slider
                      value={[weight]}
                      onValueChange={([value]) => {
                        setCategoryWeights(prev => ({
                          ...prev,
                          [key]: value
                        }));
                        setSelectedPreset(''); // Clear preset when manually adjusting
                      }}
                      min={0}
                      max={100}
                      step={5}
                      className="w-full"
                    />
                  </div>
                );
              })}

              {/* Total Weight Indicator */}
              <div className="pt-4 border-t">
                <div className="flex items-center justify-between">
                  <Label>Total Weight</Label>
                  <Badge variant={getTotalWeight() === 100 ? "default" : "destructive"}>
                    {getTotalWeight()}%
                  </Badge>
                </div>
                {getTotalWeight() !== 100 && (
                  <Alert className="mt-2">
                    <AlertTriangle className="h-4 w-4" />
                    <AlertDescription>
                      Weights should sum to 100% for optimal distribution
                    </AlertDescription>
                  </Alert>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Custom Topics Mode */}
        <TabsContent value="custom" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Add Custom Topic</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex gap-2">
                <Input
                  placeholder="Enter topic name..."
                  value={newTopicName}
                  onChange={(e) => setNewTopicName(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleAddCustomTopic()}
                />
                <Button onClick={handleAddCustomTopic}>
                  <Plus className="w-4 h-4 mr-2" />
                  Add
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center justify-between">
                <span>Custom Topics ({customTopics.length})</span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleRandomizeWeights}
                  disabled={customTopics.length === 0}
                >
                  <Shuffle className="w-4 h-4 mr-2" />
                  Randomize
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {customTopics.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <Search className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>No custom topics defined</p>
                  <p className="text-sm">Add topics above to focus learning</p>
                </div>
              ) : (
                customTopics.map((topic, index) => (
                  <div key={index} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Star className={cn("w-4 h-4", topic.color)} />
                        <Label>{topic.name}</Label>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium w-12 text-right">
                          {topic.weight}%
                        </span>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleRemoveCustomTopic(index)}
                        >
                          <Minus className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                    <Slider
                      value={[topic.weight]}
                      onValueChange={([value]) => handleCustomTopicWeightChange(index, value)}
                      min={0}
                      max={100}
                      step={5}
                      className="w-full"
                    />
                  </div>
                ))
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Action Buttons */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex justify-between items-center">
            <div className="text-sm text-muted-foreground">
              <p>Changes will affect the next learning cycle</p>
              <p>Current KB: {kbMetrics?.factCount || 0} facts</p>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => window.location.reload()}>
                <RefreshCw className="w-4 h-4 mr-2" />
                Reset
              </Button>
              <Button onClick={handleSaveConfiguration} disabled={!isConnected || saving}>
                {saving ? (
                  <>
                    <CheckCircle2 className="w-4 h-4 mr-2" />
                    Saved
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4 mr-2" />
                    Apply Configuration
                  </>
                )}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Info Alert */}
      <Alert>
        <Info className="h-4 w-4" />
        <AlertDescription>
          Topic focus affects which areas the learning engines explore. In Auto Mode,
          the system selects topics from weighted categories. In Manual Mode, only
          your custom topics are explored.
        </AlertDescription>
      </Alert>
    </div>
  );
};

export default TopicWeightConsole;
