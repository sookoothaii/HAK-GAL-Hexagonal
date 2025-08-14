# HAK-GAL HEXAGONAL Architecture Documentation

## System Overview

The HAK-GAL HEXAGONAL system is a complete refactoring of the original HAK-GAL Suite following **Clean Architecture** principles (Hexagonal/Ports & Adapters pattern).

## Directory Structure

```
HAK_GAL_HEXAGONAL/
├── frontend/                    # React/Vite Frontend (Port 5173)
│   ├── src/
│   │   ├── components/         # UI Components
│   │   ├── pages/             # Page Components
│   │   ├── services/          # API Services
│   │   ├── stores/            # Zustand State Management
│   │   ├── hooks/             # React Hooks
│   │   └── config/            # Configuration
│   └── package.json           # Dependencies
│
├── src_hexagonal/              # Backend Core (Port 5001)
│   ├── core/                  # Domain Layer
│   │   └── domain/
│   │       ├── entities.py    # Domain Entities
│   │       └── value_objects.py
│   │
│   ├── application/            # Application Layer
│   │   ├── services.py        # Use Cases
│   │   └── interfaces.py      # Port Definitions
│   │
│   ├── adapters/              # Adapters Layer
│   │   ├── api/              # REST API Adapters
│   │   ├── websocket/        # WebSocket Adapters
│   │   ├── legacy_adapters.py # HAK-GAL Bridge
│   │   ├── governor_adapter.py # Governor System
│   │   ├── llm_providers.py   # LLM Integration
│   │   └── fact_extractor.py  # Fact Processing
│   │
│   └── infrastructure/         # Infrastructure Layer
│       ├── engines/           # Learning Engines
│       │   ├── base_engine.py
│       │   ├── aethelred_engine.py
│       │   └── thesis_engine.py
│       ├── database/          # Database Access
│       ├── llm/              # LLM Providers
│       └── monitoring/        # Logging/Sentry
│
├── tests/                      # Test Suites
│   ├── unit/                  # Unit Tests
│   ├── integration/           # Integration Tests
│   └── e2e/                   # End-to-End Tests
│
├── scripts/                    # Utility Scripts
│   ├── migration/             # Migration Tools
│   └── maintenance/           # Maintenance Scripts
│
├── config/                     # Configuration Files
├── data/                       # Database & Knowledge Base
├── logs/                       # System Logs
└── docs/                       # Documentation
```

## Core Principles

### 1. Dependency Rule
Dependencies point **inward only**:
- `Infrastructure` → `Adapters` → `Application` → `Core`
- Core has no external dependencies

### 2. Port & Adapter Pattern
- **Ports**: Interfaces defined in Application layer
- **Adapters**: Implementations in Adapters layer
- Allows swapping implementations without changing core

### 3. Clean Code Principles
- **NO MOCKS**: Real results or honest errors
- **Single Responsibility**: Each module has one reason to change
- **Open/Closed**: Open for extension, closed for modification

## System Components

### Frontend (React/Vite)
- **Port**: 5173
- **Framework**: React 18 with TypeScript
- **State**: Zustand for global state
- **UI**: Radix UI + Tailwind CSS
- **WebSocket**: Socket.IO client

### Backend API (Flask)
- **Port**: 5001
- **Framework**: Flask with Socket.IO
- **Architecture**: Hexagonal (Ports & Adapters)
- **Features**:
  - RESTful API
  - WebSocket support
  - Legacy HAK-GAL integration
  - LLM providers (DeepSeek, Gemini, Mistral)
  - CUDA-accelerated reasoning

### Learning Engines
- **Aethelred Engine**: Fact generation via LLM
- **Thesis Engine**: Pattern analysis and meta-knowledge
- **Governor**: Thompson Sampling strategy management

### Knowledge System
- **Database**: SQLite (k_assistant.db)
- **Format**: Predicate(Entity1, Entity2) facts
- **Reasoning**: Neural + Symbolic (HRM system)
- **Search**: Semantic search with CUDA acceleration

## API Endpoints

### Core Endpoints
```
GET  /health                - System health
GET  /api/status            - Detailed status
GET  /api/facts             - List facts
POST /api/facts             - Add fact
POST /api/search            - Search facts
POST /api/reason            - Neural reasoning
```

### LLM Endpoints
```
POST /api/llm/get-explanation - Get LLM explanation
POST /api/command             - Process commands
```

### WebSocket Events
```
connection_status           - Client connection
kb_update                  - Knowledge base updates
kb_metrics                 - Metrics updates
governor_update            - Governor status
```

## Configuration

### Environment Variables (.env)
```env
# LLM Providers
DEEPSEEK_API_KEY=sk-xxx
GEMINI_API_KEY=xxx
MISTRAL_API_KEY=xxx

# System
HEXAGONAL_PORT=5001
FRONTEND_PORT=5173

# Features
ENABLE_GOVERNOR=true
ENABLE_ENGINES=true
ENABLE_CUDA=true
```

### Frontend Configuration
- Default backend: HEXAGONAL (port 5001)
- Can switch between Original (5000) and HEXAGONAL (5001)
- Configured in `frontend/src/config/backends.ts`

## Running the System

### Complete System Start
```batch
# Run from HAK_GAL_HEXAGONAL directory
start_hexagonal_complete.bat
```

### Individual Components
```batch
# Backend only
python src_hexagonal\hexagonal_api_enhanced_clean.py

# Frontend only
cd frontend && npm run dev

# Engines (via Governor or standalone)
python src_hexagonal\infrastructure\engines\aethelred_engine.py -p 5001
python src_hexagonal\infrastructure\engines\thesis_engine.py -p 5001
```

## Development Guidelines

### Adding New Features
1. Define interface in `application/interfaces.py`
2. Implement adapter in `adapters/`
3. Add infrastructure if needed in `infrastructure/`
4. Write tests in `tests/`
5. Update documentation

### Code Style
- Python: PEP 8 with type hints
- TypeScript: ESLint + Prettier
- Comments: HAK/GAL Verfassung references where applicable

### Testing Strategy
- Unit tests for Core/Application
- Integration tests for Adapters
- E2E tests for critical flows
- Coverage target: >80%

## Monitoring & Debugging

### Logs
- Backend logs: Console output + `logs/backend.log`
- Frontend logs: Browser console
- Engine logs: Console output with timestamps

### Performance Metrics
- API response times: <20ms target
- CUDA memory: Monitor via `nvidia-smi`
- Knowledge base size: Track via `/api/facts/count`

### Error Handling
- 503 for unavailable services (honest errors)
- Clear error messages
- No fake data or mock responses

## Migration from Original HAK-GAL

### Data Migration
```batch
# Run migration script
migrate_complete_system.bat

# Update configuration
python update_frontend_config.py
```

### Feature Parity Checklist
- [x] Knowledge base management
- [x] Neural reasoning (HRM)
- [x] LLM integration
- [x] Learning engines
- [x] Governor system
- [x] WebSocket real-time updates
- [x] CUDA acceleration
- [ ] Complete graph generation
- [ ] Backup system
- [ ] Multi-user support

## References

- Original HAK-GAL: `D:\MCP Mods\HAK_GAL_SUITE`
- HAK/GAL Verfassung: See `HAK_GAL_VERFASSUNG_UND_ARCHITEKTUR.md`
- Clean Architecture: Robert C. Martin
- Hexagonal Architecture: Alistair Cockburn

---

*Last Updated: 2025-08-13*
*Version: 1.0.0*
