# WORKFLOW PRO - QUICK REFERENCE & TROUBLESHOOTING

## COMMON ISSUES & FIXES

### **Issue: ReactFlow edges not visible**
```javascript
// FIX: Add Handle components
import { Handle, Position } from 'reactflow';

<Handle type="target" position={Position.Left} id="input" />
[Node Content]
<Handle type="source" position={Position.Right} id="output" />
```

### **Issue: EventEmitter not working in browser**
```javascript
// FIX: Custom browser implementation
class EventEmitter {
  private events: Map<string, Set<Function>> = new Map();
  on(event, handler) { ... }
  emit(event, ...args) { ... }
}
```

### **Issue: API calls failing (400/405)**
```javascript
// FIX: Use correct endpoints
GET /api/facts/count       // not /api/mcp
GET /api/facts/search?q=   // with query param
GET /api/status            // for health check
```

### **Issue: Variables used before initialization**
```javascript
// WRONG
const mode = options.dryRun;  // options not defined yet
const options = { ... };

// RIGHT
const options = { ... };
const mode = options.dryRun;
```

## QUICK START COMMANDS

```bash
# Start frontend
cd frontend
npm run dev

# Open workflow
http://localhost:5173/workflow

# Test workflow
1. Click "Demo" button
2. Click "Execute" button (dry-run safe)
3. Check logs on right panel
```

## NODE CONNECTION GUIDE

```
OUTPUT (Right) ──────> INPUT (Left)
     ●                    ●
   Source              Target
```

## EXECUTION MODES

| Mode | Description | Safe? |
|------|------------|-------|
| **Dry Run** | No operations executed | ✅ Yes |
| **Live** | Operations execute | ⚠️ With protection |
| **Write Enabled** | Allows writes | ❌ Use carefully |

## MCP TOOL CATEGORIES

- 🟢 **Knowledge Base** - 14 tools (safe)
- 🟣 **AI Delegation** - 3 tools (API calls)
- 🔵 **File Operations** - 13 tools (filesystem)
- 🟡 **Execution** - 3 tools (code run)
- 🔴 **Write Operations** - Require approval
- ⚪ **Flow Control** - 3 tools (logic)

## KEY FILES

```
frontend/src/
├── workflow-system/
│   ├── core/engine/WorkflowEngine.ts
│   └── services/MCPWorkflowService.ts
└── pages/WorkflowPro.tsx
```

## PERFORMANCE TARGETS

- Node render: <16ms ✅
- API calls: <100ms ✅  
- Parallel nodes: 3 ✅
- Memory: <50MB ✅

---
**Last Updated:** September 5, 2025
**Version:** 2.0 Production