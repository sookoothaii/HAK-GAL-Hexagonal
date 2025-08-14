# HRM Frontend Integration Guide

## Übersicht der Änderungen

Das Frontend wurde um vollständige HRM (Hierarchical Reasoning Model) Unterstützung erweitert.

## Neue Dateien

1. **`src/stores/useHRMStore.ts`**
   - Separater Store für HRM-Daten
   - Verwaltet Metriken, Query-History, Training-Status

2. **`src/hooks/useHRMSocket.ts`**
   - WebSocket-Integration für HRM-Events
   - Sendet Queries und empfängt Results

3. **`src/components/dashboard/HRMDashboard.tsx`**
   - Dashboard-Widget für HRM-Metriken
   - Zeigt Confidence Gap, Model Status, Performance

4. **`src/components/interaction/HRMQueryInterface.tsx`**
   - Neue Query-Interface für HRM
   - Single & Batch Query Support

## Integration in ProApp.tsx

```typescript
// In ProApp.tsx hinzufügen:

// Imports
import { useHRMSocket } from '@/hooks/useHRMSocket';
import HRMDashboard from '@/components/dashboard/HRMDashboard';
import HRMQueryInterface from '@/components/interaction/HRMQueryInterface';

// In AppContent function:
function AppContent() {
  // ... existing code ...
  
  // Add HRM Socket Hook
  useHRMSocket();
  useGovernorSocket();
  
  // ... rest of code ...
}

// Add new routes:
<Route path="/hrm" element={<HRMQueryInterface />} />
<Route path="/hrm/dashboard" element={<HRMDashboard />} />
```

## Integration in ProDashboard.tsx

```typescript
// In ProDashboard.tsx hinzufügen:

import HRMDashboard from '@/components/dashboard/HRMDashboard';

// In der Dashboard-Grid einfügen:
<div className="col-span-12">
  <HRMDashboard />
</div>
```

## Integration in ProNavigation.tsx

```typescript
// Neue Navigation Items hinzufügen:

const hrmItems = [
  {
    title: "HRM Query",
    href: "/hrm",
    icon: Brain,
    description: "Neural Reasoning Interface"
  },
  {
    title: "HRM Dashboard",
    href: "/hrm/dashboard", 
    icon: Activity,
    description: "Model Metrics & Performance"
  }
];
```

## Store Updates

Der bestehende `useGovernorStore` kann optional mit HRM-Daten erweitert werden:

```typescript
// In useGovernorStore.ts:
import { useHRMStore } from './useHRMStore';

// HRM State als Teil des Governor Store
interface GovernorState {
  // ... existing state ...
  
  // HRM Integration
  getHRMMetrics: () => any;
}

// In der Implementation:
getHRMMetrics: () => {
  return useHRMStore.getState().hrm.metrics;
}
```

## WebSocket Events

Folgende neue Events werden unterstützt:

**Empfangen:**
- `hrm_status` - Model Status Update
- `hrm_result` - Query Result  
- `hrm_batch_result` - Batch Processing Result
- `hrm_metrics` - Prometheus Metrics
- `hrm_training_status` - Training Status
- `hrm_error` - Error Messages

**Senden:**
- `hrm_reason` - Single Query
- `hrm_batch_reason` - Batch Queries
- `hrm_metrics_request` - Request Metrics
- `hrm_status_request` - Request Status

## NPM Dependencies

Keine neuen Dependencies erforderlich! Alle verwendeten Komponenten sind bereits installiert:
- zustand (State Management)
- socket.io-client (WebSocket)
- framer-motion (Animations)
- lucide-react (Icons)
- sonner (Toast Notifications)

## Testing

1. **Backend muss laufen mit HRM:**
   ```bash
   python src/hak_gal/api.py
   ```

2. **Frontend starten:**
   ```bash
   npm run dev
   ```

3. **Test-Queries:**
   - "IsA(Socrates, Philosopher)" - Expected: >85% confidence
   - "HasPart(Computer, CPU)" - Expected: >85% confidence
   - "IsA(Water, Person)" - Expected: <15% confidence

## Performance Targets

- **Query Response:** <10ms (GPU)
- **Batch Processing:** <100ms für 10 Queries
- **WebSocket Latency:** <5ms
- **UI Update:** 60fps

## Troubleshooting

**Problem:** HRM Store zeigt keine Daten
- **Lösung:** Prüfen ob Backend HRM geladen hat (Logs checken)

**Problem:** WebSocket Events kommen nicht an
- **Lösung:** Browser Console für Errors checken, Port 5000 verfügbar?

**Problem:** Queries returnen immer 0% confidence
- **Lösung:** Model nicht geladen, Backend neu starten

## Nächste Schritte

1. **ProApp.tsx** updaten mit HRM Routes
2. **ProNavigation.tsx** erweitern mit HRM Links
3. **ProDashboard.tsx** HRM Widget einbauen
4. **Frontend neu builden** mit `npm run build`

## Empirische Validierung

Nach Integration sollten folgende Metriken sichtbar sein:
- Model Status: "operational"
- Parameters: 572,673
- Vocabulary: 694  
- Confidence Gap: ~80.2%
- Device: "cuda"

Alle Komponenten sind HAK/GAL Verfassung-konform implementiert.
