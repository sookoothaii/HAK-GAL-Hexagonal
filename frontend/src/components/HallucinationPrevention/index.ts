// Hallucination Prevention Module Exports
export { HallucinationPrevention as default } from './HallucinationPrevention';
export { BatchProcessingTab } from './BatchProcessingTab';
export { GovernanceTab } from './GovernanceTab';

// Re-export service for convenience
export { hallucinationAPI } from '@/services/hallucinationPreventionService';
export type { 
  ValidationResult, 
  BatchValidationResult, 
  QualityAnalysisResult, 
  Statistics 
} from '@/services/hallucinationPreventionService';
