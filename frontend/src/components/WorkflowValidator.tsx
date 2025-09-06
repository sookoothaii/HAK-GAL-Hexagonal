import React, { useState, useEffect } from 'react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, XCircle, AlertTriangle, Info } from 'lucide-react';

interface ValidationError {
  path: string;
  message: string;
  severity: 'error' | 'warning' | 'info';
}

interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
  warnings: ValidationError[];
  info: ValidationError[];
  schemaVersion?: string;
  validatedAt: string;
}

interface WorkflowValidatorProps {
  workflowData: any;
  onValidationComplete: (result: ValidationResult) => void;
  showDetails?: boolean;
}

export function WorkflowValidator({ 
  workflowData, 
  onValidationComplete, 
  showDetails = false 
}: WorkflowValidatorProps) {
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);
  const [isValidating, setIsValidating] = useState(false);
  const [schema, setSchema] = useState<any>(null);

  // Load schema dynamically
  useEffect(() => {
    const loadSchema = async () => {
      try {
        // Try to load the workflow schema
        const response = await fetch('/workflow/workflow.schema.json');
        if (response.ok) {
          const schemaData = await response.json();
          setSchema(schemaData);
        } else {
          // Fallback to basic validation if no schema
          setSchema(null);
        }
      } catch (error) {
        console.warn('Schema loading failed, using basic validation:', error);
        setSchema(null);
      }
    };

    loadSchema();
  }, []);

  // Basic validation rules (fallback when no schema)
  const basicValidation = (data: any): ValidationResult => {
    const errors: ValidationError[] = [];
    const warnings: ValidationError[] = [];
    const info: ValidationError[] = [];

    // Check if data exists
    if (!data) {
      errors.push({
        path: 'root',
        message: 'Workflow data is missing',
        severity: 'error'
      });
      return { isValid: false, errors, warnings, info, validatedAt: new Date().toISOString() };
    }

    // Check for required top-level properties
    if (!data.nodes || !Array.isArray(data.nodes)) {
      errors.push({
        path: 'nodes',
        message: 'Workflow must have a nodes array',
        severity: 'error'
      });
    }

    if (!data.edges || !Array.isArray(data.edges)) {
      errors.push({
        path: 'edges',
        message: 'Workflow must have an edges array',
        severity: 'error'
      });
    }

    // Validate nodes
    if (data.nodes && Array.isArray(data.nodes)) {
      data.nodes.forEach((node: any, index: number) => {
        if (!node.id) {
          errors.push({
            path: `nodes[${index}]`,
            message: 'Node must have an ID',
            severity: 'error'
          });
        }
        
        if (!node.type && !node.name) {
          warnings.push({
            path: `nodes[${index}]`,
            message: 'Node should have a type or name',
            severity: 'warning'
          });
        }

        if (node.position && (typeof node.position.x !== 'number' || typeof node.position.y !== 'number')) {
          warnings.push({
            path: `nodes[${index}].position`,
            message: 'Node position should have numeric x and y coordinates',
            severity: 'warning'
          });
        }
      });
    }

    // Validate edges
    if (data.edges && Array.isArray(data.edges)) {
      data.edges.forEach((edge: any, index: number) => {
        if (!edge.source || !edge.target) {
          errors.push({
            path: `edges[${index}]`,
            message: 'Edge must have source and target',
            severity: 'error'
          });
        }
      });
    }

    // Check for orphaned nodes
    if (data.nodes && data.edges) {
      const nodeIds = new Set(data.nodes.map((n: any) => n.id));
      const connectedNodeIds = new Set();
      
      data.edges.forEach((edge: any) => {
        connectedNodeIds.add(edge.source);
        connectedNodeIds.add(edge.target);
      });

      const orphanedNodes = Array.from(nodeIds).filter(id => !connectedNodeIds.has(id));
      if (orphanedNodes.length > 0) {
        warnings.push({
          path: 'connectivity',
          message: `Found ${orphanedNodes.length} orphaned nodes: ${orphanedNodes.join(', ')}`,
          severity: 'warning'
        });
      }
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings,
      info,
      validatedAt: new Date().toISOString()
    };
  };

  // Schema-based validation using Claude's JSON Schema
  const schemaValidation = async (data: any, schema: any): Promise<ValidationResult> => {
    try {
      const errors: ValidationError[] = [];
      const warnings: ValidationError[] = [];
      const info: ValidationError[] = [];
      
      // Validate required top-level properties
      if (!data.workflow_id) {
        errors.push({
          path: 'workflow_id',
          message: 'Workflow ID is required (format: wf-name-variant)',
          severity: 'error'
        });
      } else if (!/^wf-[a-z0-9-]+$/.test(data.workflow_id)) {
        errors.push({
          path: 'workflow_id',
          message: 'Workflow ID must match pattern: wf-name-variant',
          severity: 'error'
        });
      }
      
      if (!data.version) {
        errors.push({
          path: 'version',
          message: 'Version is required (format: x.y.z)',
          severity: 'error'
        });
      } else if (!/^\d+\.\d+\.\d+$/.test(data.version)) {
        errors.push({
          path: 'version',
          message: 'Version must match semantic versioning (x.y.z)',
          severity: 'error'
        });
      }
      
      if (!data.ssot_id) {
        errors.push({
          path: 'ssot_id',
          message: 'SSoT ID is required (12-char SHA256 hash)',
          severity: 'error'
        });
      } else if (!/^[a-f0-9]{12}$/.test(data.ssot_id)) {
        errors.push({
          path: 'ssot_id',
          message: 'SSoT ID must be 12-char SHA256 hash',
          severity: 'error'
        });
      }
      
      // Validate nodes with enhanced rules
      if (data.nodes && Array.isArray(data.nodes)) {
        data.nodes.forEach((node: any, index: number) => {
          if (!node.id) {
            errors.push({
              path: `nodes[${index}]`,
              message: 'Node must have an ID (format: node-name)',
              severity: 'error'
            });
          } else if (!/^node-[a-z0-9-]+$/.test(node.id)) {
            errors.push({
              path: `nodes[${index}]`,
              message: 'Node ID must match pattern: node-name',
              severity: 'error'
            });
          }
          
          if (!node.type) {
            errors.push({
              path: `nodes[${index}]`,
              message: 'Node must have a type',
              severity: 'error'
            });
          }
          
          if (!node.position || typeof node.position.x !== 'number' || typeof node.position.y !== 'number') {
            errors.push({
              path: `nodes[${index}].position`,
              message: 'Node must have numeric x and y coordinates',
              severity: 'error'
            });
          }
          
          // Check for approval requirements
          if (node.approval && node.approval.required) {
            info.push({
              path: `nodes[${index}].approval`,
              message: `Node requires approval: ${node.approval.message || 'No message specified'}`,
              severity: 'info'
            });
          }
          
          // Check for timeout settings
          if (node.timeout && (node.timeout < 1 || node.timeout > 600)) {
            warnings.push({
              path: `nodes[${index}].timeout`,
              message: 'Timeout should be between 1-600 seconds',
              severity: 'warning'
            });
          }
        });
      }
      
      // Validate edges with enhanced rules
      if (data.edges && Array.isArray(data.edges)) {
        data.edges.forEach((edge: any, index: number) => {
          if (!edge.id) {
            errors.push({
              path: `edges[${index}]`,
              message: 'Edge must have an ID (format: edge-name)',
              severity: 'error'
            });
          } else if (!/^edge-[a-z0-9-]+$/.test(edge.id)) {
            errors.push({
              path: `edges[${index}]`,
              message: 'Edge ID must match pattern: edge-name',
              severity: 'error'
            });
          }
          
          if (!edge.source || !edge.target) {
            errors.push({
              path: `edges[${index}]`,
              message: 'Edge must have source and target',
              severity: 'error'
            });
          }
          
          // Check for conditional edges
          if (edge.condition) {
            info.push({
              path: `edges[${index}].condition`,
              message: `Edge has conditional logic: ${edge.condition}`,
              severity: 'info'
            });
          }
        });
      }
      
      // Check approval policies
      if (data.approvals) {
        if (data.approvals.default_policy === 'deny_writes') {
          info.push({
            path: 'approvals.default_policy',
            message: 'Default policy: Write operations require explicit approval',
            severity: 'info'
          });
        }
        
        if (data.approvals.write_nodes_require_approval) {
          info.push({
            path: 'approvals.write_nodes_require_approval',
            message: 'Write nodes require approval',
            severity: 'info'
          });
        }
      }
      
      // Check execution mode
      if (data.execution) {
        if (data.execution.dry_run) {
          info.push({
            path: 'execution.dry_run',
            message: 'Dry-run mode enabled - no actual changes will be made',
            severity: 'info'
          });
        }
        
        if (data.execution.mode === 'parallel' && data.execution.max_parallel > 5) {
          warnings.push({
            path: 'execution.max_parallel',
            message: 'High parallel execution may impact system performance',
            severity: 'warning'
          });
        }
      }
      
      return {
        isValid: errors.length === 0,
        errors,
        warnings,
        info,
        schemaVersion: schema.version || 'unknown',
        validatedAt: new Date().toISOString()
      };
      
    } catch (error) {
      console.error('Schema validation failed:', error);
      return basicValidation(data);
    }
  };

  const validateWorkflow = async () => {
    setIsValidating(true);
    
    try {
      let result: ValidationResult;
      
      if (schema) {
        result = await schemaValidation(workflowData, schema);
      } else {
        result = basicValidation(workflowData);
      }
      
      setValidationResult(result);
      onValidationComplete(result);
    } catch (error) {
      console.error('Validation failed:', error);
      const errorResult: ValidationResult = {
        isValid: false,
        errors: [{
          path: 'validation',
          message: `Validation failed: ${error}`,
          severity: 'error'
        }],
        warnings: [],
        info: [],
        validatedAt: new Date().toISOString()
      };
      setValidationResult(errorResult);
      onValidationComplete(errorResult);
    } finally {
      setIsValidating(false);
    }
  };

  // Auto-validate when workflow data changes
  useEffect(() => {
    if (workflowData && Object.keys(workflowData).length > 0) {
      validateWorkflow();
    }
  }, [workflowData]);

  if (!validationResult) {
    return (
      <Card className="p-4">
        <div className="flex items-center gap-2">
          <Info className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm text-muted-foreground">Validating workflow...</span>
        </div>
      </Card>
    );
  }

  const { isValid, errors, warnings, info, schemaVersion } = validationResult;

  return (
    <Card className="p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-sm">Workflow Validation</h3>
        <div className="flex items-center gap-2">
          {schemaVersion && (
            <Badge variant="outline" className="text-xs">
              Schema v{schemaVersion}
            </Badge>
          )}
          <Badge 
            variant={isValid ? "default" : "destructive"}
            className="text-xs"
          >
            {isValid ? "Valid" : "Invalid"}
          </Badge>
        </div>
      </div>

      {/* Validation Summary */}
      <div className="space-y-2 mb-3">
        {errors.length > 0 && (
          <Alert variant="destructive" className="py-2">
            <XCircle className="h-4 w-4" />
            <AlertDescription className="text-xs">
              {errors.length} validation error{errors.length !== 1 ? 's' : ''}
            </AlertDescription>
          </Alert>
        )}
        
        {warnings.length > 0 && (
          <Alert variant="default" className="py-2 bg-yellow-50 border-yellow-200">
            <AlertTriangle className="h-4 w-4 text-yellow-600" />
            <AlertDescription className="text-xs text-yellow-800">
              {warnings.length} warning{warnings.length !== 1 ? 's' : ''}
            </AlertDescription>
          </Alert>
        )}
        
        {isValid && errors.length === 0 && warnings.length === 0 && (
          <Alert className="py-2 bg-green-50 border-green-200">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-xs text-green-800">
              Workflow is valid and ready to run
            </AlertDescription>
          </Alert>
        )}
      </div>

      {/* Detailed Validation Results */}
      {showDetails && (errors.length > 0 || warnings.length > 0 || info.length > 0) && (
        <div className="space-y-2">
          <h4 className="text-sm font-medium">Details:</h4>
          
          {errors.map((error, index) => (
            <div key={`error-${index}`} className="text-xs p-2 bg-red-50 border border-red-200 rounded">
              <div className="flex items-center gap-2">
                <XCircle className="h-3 w-3 text-red-600" />
                <span className="font-medium text-red-800">{error.path}</span>
              </div>
              <p className="text-red-700 mt-1">{error.message}</p>
            </div>
          ))}
          
          {warnings.map((warning, index) => (
            <div key={`warning-${index}`} className="text-xs p-2 bg-yellow-50 border border-yellow-200 rounded">
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-3 w-3 text-yellow-600" />
                <span className="font-medium text-yellow-800">{warning.path}</span>
              </div>
              <p className="text-yellow-700 mt-1">{warning.message}</p>
            </div>
          ))}
          
          {info.map((infoItem, index) => (
            <div key={`info-${index}`} className="text-xs p-2 bg-blue-50 border border-blue-200 rounded">
              <div className="flex items-center gap-2">
                <Info className="h-3 w-3 text-blue-600" />
                <span className="font-medium text-blue-800">{infoItem.path}</span>
              </div>
              <p className="text-blue-700 mt-1">{infoItem.message}</p>
            </div>
          ))}
        </div>
      )}

      {/* Re-validate Button */}
      <div className="mt-3">
        <Button 
          onClick={validateWorkflow} 
          disabled={isValidating}
          size="sm" 
          variant="outline"
          className="w-full"
        >
          {isValidating ? "Validating..." : "Re-validate"}
        </Button>
      </div>
    </Card>
  );
}
