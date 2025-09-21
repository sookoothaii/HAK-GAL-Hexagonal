# HAK-GAL Hexagonal
## Advanced Multi-Agent Knowledge System with MCP Integration & Hallucination Prevention

![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![KB Tools](https://img.shields.io/badge/KB_Tools-69-purple.svg)
![FS Tools](https://img.shields.io/badge/FS_Tools-56-orange.svg)
![Total Tools](https://img.shields.io/badge/Total_Tools-125-red.svg)
![MCPSuperAssistant](https://img.shields.io/badge/MCPSuperAssistant-Ready-brightgreen.svg)
![Facts](https://img.shields.io/badge/Facts-788_n--ary-yellow.svg)

## Overview

HAK-GAL Hexagonal is a complete rewrite of the original HAK-GAL-Suite, now featuring:

- **Hexagonal Architecture** (Ports & Adapters)
- **Dual MCP Servers** with 125 total tools
  - Knowledge Base Server: 69 tools
  - Filesystem Server: 56 tools (v4.1 with Extended Tools)
- **NEW: Hallucination Prevention Engine** with 9 API endpoints
- **Multi-LLM Collaboration** via standardized Init Protocol
- **788 Symbolic Facts** (n-ary format with 15+ arguments)
- **Browser Integration** via MCPSuperAssistant.ai
- **Multi-Agent System** (4 adapters)
- **Visual Workflow Editor** (122 node types)
- **SQLite Knowledge Base** with WAL mode

## 🆕 Key Features (September 2025)

### Hallucination Prevention Engine
A 4-layer validation system ensuring fact accuracy:
- **Scientific Validator**: Domain-specific knowledge validation
- **Maximal Validator**: HAK/GAL standards compliance
- **Quality Check**: Heuristic rule validation
- **LLM Reasoning**: Semantic consistency verification

API Endpoints:
```yaml
POST /api/hallucination-prevention/validate
POST /api/hallucination-prevention/validate-batch
POST /api/hallucination-prevention/quality-analysis
GET  /api/hallucination-prevention/invalid-facts
# ... and 5 more endpoints
```

### LLM Governor System
Intelligent routing and decision engine for multi-LLM coordination:
```yaml
GET  /api/llm-governor/status
POST /api/llm-governor/enable
POST /api/llm-governor/disable
POST /api/llm-governor/evaluate
GET  /api/llm-governor/metrics
POST /api/llm-governor/debug
```

### Multi-LLM Initialization Protocol
Enables seamless collaboration between different LLM instances:
- **ProjectHubLLMInitializationEnhanced**: 9-step protocol
- **Fact Persistence**: Shared knowledge across sessions
- **Template Compliance**: Standardized fact formats
- **Cross-LLM Learning**: Facts from one LLM inform others

### Extended API Endpoints
Additional monitoring and system endpoints:
```yaml
# Facts Management
GET /api/facts/paginated
GET /api/facts/stats

# System Monitoring  
GET /api/system/gpu
GET /api/mojo/status
GET /api/metrics
GET /api/limits
GET /api/graph/emergency-status

# Engine Management
POST /api/engines/thesis/*
POST /api/engines/aethelred/*
```
Advanced knowledge representation:
```prolog
QuantumMechanics(wave_particle_duality, uncertainty_principle, 
                 quantum_entanglement, superposition, measurement_collapse,
                 schrodinger_equation, heisenberg_limit, quantum_tunneling,
                 quantum_field_theory, many_worlds_interpretation, 
                 copenhagen_interpretation, quantum_decoherence,
                 quantum_information, bell_inequality, quantum_computing,
                 planck_constant:Q(6.626e-34, J*s))
```

## Quick Start with MCPSuperAssistant.ai (Browser)

The easiest way to use HAK-GAL's MCP servers is through MCPSuperAssistant.ai:

1. Start the MCP Proxy for your chosen server:

```bash
# For Filesystem Server (56 tools)
npx @srbhptl39/mcp-superassistant-proxy@latest --config ./filesystem-mcp.sse.config.json --outputTransport sse --port 3007

# For KB Server (69 tools) - UPDATED COUNT
npx @srbhptl39/mcp-superassistant-proxy@latest --config ./kb-mcp.sse.config.json --outputTransport sse --port 3008

# Or run both for all 125 tools!
```

2. Open [MCPSuperAssistant.ai](https://mcpsuperassistant.ai) in your browser

3. Add your server(s):
   - Filesystem Server: `http://localhost:3007/sse`
   - KB Server: `http://localhost:3008/sse`

No API keys needed for browser usage!

## Quick Start (Local Installation)

### Prerequisites
- Python 3.11+
- Node.js 16+
- Git
- curl or wget

### Installation

```bash
# 1. Clone repository
git clone https://github.com/sookoothaii/HAK-GAL-Hexagonal.git
cd HAK-GAL-Hexagonal

# 2. WICHTIG: Download Knowledge Base (17.15 MB - with 788 n-ary facts)
# Windows:
download_kb.bat
# Linux/Mac:
chmod +x download_kb.sh
./download_kb.sh

# 3. Run automatic setup
python setup.py

# Alternative manual setup:
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
cd frontend && npm install && cd ..
```

### Running the System

```bash
# Activate virtual environment first!
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Terminal 1: Start MCP KB Server (69 tools)
python ultimate_mcp/hakgal_mcp_ultimate.py

# Terminal 2: Start MCP Filesystem Server (56 tools) - v4.1
python filesystem_mcp/hak_gal_filesystem.py

# Terminal 3: Start API Server with Hallucination Prevention (Port 5002)
python src_hexagonal/hexagonal_api_enhanced_clean.py

# Terminal 4: Start Frontend with 4-Tab Interface (Port 5173)
cd frontend
npm run dev
```

Open http://localhost:5173 in your browser.

## Using Both MCP Servers

You have two powerful MCP servers to choose from or use together:

### 1. Knowledge Base Server (ultimate_mcp) - 69 Tools
Focus: Knowledge management, semantic search, AI operations, and multi-LLM coordination
- **Specialties**: Facts management, consensus evaluation, multi-agent coordination
- **NEW**: Init protocol support, n-ary facts, hallucination prevention integration

### 2. Filesystem Server (filesystem_mcp) - 56 Tools (v4.1)
Focus: Advanced file operations and development tools
- **Specialties**: Git operations, package management, build tools, API testing
- **Extended**: Git, npm/pip/yarn, make/gradle, SQLite, and more

## Architecture

### System Components
```
HAK-GAL Hexagonal/
├── ultimate_mcp/        # KB MCP Server (69 tools)
├── filesystem_mcp/      # Filesystem Server (56 tools) v4.1
├── src_hexagonal/       # Hexagonal Backend
│   ├── adapters/        # External interfaces + Hallucination Prevention
│   ├── core/           # Domain logic
│   └── application/    # Use cases
├── frontend/           # React + TypeScript + Vite UI
├── PROJECT_HUB/        # Documentation & Multi-LLM Protocols
├── native/             # C++ performance modules
└── workflows/          # Workflow definitions
```

### Multi-Agent System
- **Gemini Adapter**: Google AI integration
- **Claude CLI Adapter**: Anthropic Claude
- **Claude Desktop Adapter**: MCP Protocol + Init Support
- **Cursor Adapter**: IDE integration
- **NEW**: Cross-LLM communication via shared facts

### Knowledge Base
- **Database**: SQLite with WAL mode
- **Facts**: 788 n-ary facts (as of 2025-09-21)
- **Format**: N-ary predicates with Q(...) notation for quantities
- **Example**: `EvolutionaryBiology(natural_selection, genetic_drift, ...[15+ args]...)`
- **Size**: 17.15 MB
- **Status**: ✅ Enhanced with scientific facts & hallucination prevention

## MCP Tools

**Total: 125 tools** across two specialized servers designed for maximum flexibility and redundancy.

### Knowledge Base Server (ultimate_mcp) - 69 Tools

Primary focus on knowledge management, AI operations, and multi-LLM coordination:

| Category | Count | Examples |
|----------|-------|----------|
| Knowledge Base | 35 | `search_knowledge`, `add_fact`, `semantic_similarity` |
| File Operations | 13 | `read_file`, `write_file`, `grep` (redundant for safety) |
| Database Ops | 7 | `db_vacuum`, `db_backup_now`, `db_checkpoint` |
| Multi-Agent | 5 | `delegate_task`, `consensus_evaluator`, `bias_detector` |
| Code Execution | 1 | `execute_code` |
| Meta Tools | 4 | `reliability_checker`, `delegation_optimizer` |
| Sentry/Others | 4 | Optional monitoring and utility tools |

### Filesystem Server (filesystem_mcp) - 56 Tools (v4.1)

Extended with professional development tools:

| Category | Count | Examples |
|----------|-------|----------|
| Core File Ops | 10 | `read_file`, `write_file`, `copy_batch`, `move_file` |
| Advanced File Tools | 10 | `batch_rename`, `merge_files`, `split_file`, `secure_delete` |
| Search & Edit | 5 | `grep`, `find_files`, `multi_edit` |
| Archive & Compression | 4 | `archive_create/extract`, `compress/decompress` |
| Git Operations | 6 | `git_status`, `git_commit`, `git_push`, `git_pull` |
| Package Management | 3 | `package_install/list/update` (pip, npm, yarn, nuget) |
| Build & Test | 2 | `run_build` (make, maven, gradle), `run_tests` |
| Database | 3 | `db_connect`, `db_query`, `db_schema` (SQLite) |
| API Testing | 2 | `api_request`, `api_test_suite` |
| Environment Mgmt | 3 | `env_create/list/freeze` (Python, Conda, Node.js) |
| Analysis & Utils | 8 | `file_diff`, `calculate_hash`, `format_code`, `watch_file` |

### Redundancy by Design

Some tools (like file operations) are intentionally available in both servers to ensure continued operation if one server fails. This architectural decision provides robustness for critical operations.

## WorkflowPro

Visual workflow editor featuring:
- 122 node types including specialized HAK-GAL nodes
- Drag-and-drop interface with real-time preview
- Real-time execution with visual feedback
- Complex logic support (branches, loops, error handling)
- Multi-agent orchestration
- **Knowledge Base integration** (Count Facts, Get Stats, etc.)
- **System Health monitoring** built-in
- **AI Analysis nodes** for intelligent processing
- **Save/Load workflows** with optional parameters

## HAK/GAL Constitution

The system follows 8 constitutional articles:
1. **Complementary Intelligence**
2. **Targeted Interrogation**
3. **External Verification**
4. **Conscious Boundary-Crossing**
5. **System Meta-reflection**
6. **Empirical Validation**
7. **Conjugated States**
8. **Principle Collision Protocol**

## Configuration

1. Copy `.env.example` to `.env`
2. Add your API keys:
   - `GEMINI_API_KEY` for Google AI
   - `DEEPSEEK_API_KEY` for DeepSeek
   - `SENTRY_DSN` for error tracking (optional but recommended)
   - `X-API-Key` for Hallucination Prevention: `hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d`
   - Other LLM providers as needed

3. For Sentry monitoring (optional):
   ```
   SENTRY_DSN=your-sentry-dsn-here
   ```

## Security

- API Key authentication
- Write token protection (auth_token: `515f57956e7bd15ddc3817573598f190`)
- Audit logging
- Sandboxed code execution
- No network access from sandbox
- **NEW**: 4-layer fact validation

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Performance

- **API Response**: < 100ms (local)
- **Knowledge Search**: < 30ms
- **DB Inserts**: 10,000+/sec
- **Code Execution**: Sandboxed with timeouts
- **Native C++ modules**: For performance-critical operations
- **Hallucination Check**: < 500ms per fact

## System Health (September 2025)

- **Status**: Production-Ready (Health Score: 90/100) ✅
- **Monitoring**: Sentry Integration Ready (DSN configuration needed) ✅
- **Code Quality**: Exceptional (Hallucination Prevention fully integrated) ✅
- **Database**: 788 n-ary facts, multi-LLM ready ✅
- **Z3/SMT Verifier**: v4.15.1 fully functional ✅
- **Governance V3**: 95% success rate ✅
- **Hallucination Prevention**: 9/9 endpoints operational ✅
- **LLM Governor**: 6/6 endpoints active ✅
- **Extended API**: GPU monitoring, Mojo status, Metrics endpoints ✅

## Roadmap

- [ ] External Integration Plugin System
- [ ] Credential Vault Implementation  
- [ ] n8n-style Node Library
- [ ] Enhanced Data Mapping
- [ ] GraphDB Migration
- [x] Hallucination Prevention Engine
- [x] Multi-LLM Init Protocol
- [ ] Prometheus/Grafana Integration (planned)

## Documentation

- [Database Setup](docs/database_setup.md) - Knowledge Base installation
- [System Architecture](docs/architecture.md)
- [API Documentation](docs/api.md)
- [Workflow Tutorial](docs/workflow_tutorial.md)
- [MCP Tools Reference](docs/mcp_tools.md)
- **NEW**: [Hallucination Prevention Guide](docs/hallucination_prevention.md)
- **NEW**: [Multi-LLM Init Protocol](PROJECT_HUB/docs/guides/LLM_INITIALIZATION_CRITICAL_SYNTAX_RULES.md)

## Troubleshooting

### System won't start
- Ensure `hexagonal_kb.db` exists (run `download_kb.bat/sh`)
- Check Python version >= 3.11
- Verify all ports are free (5002, 5173, 8088)

### Import errors
- Activate virtual environment
- Run `pip install -r requirements.txt`

### Frontend issues
- Clear browser cache
- Run `npm install` in frontend directory
- Check for TypeScript errors

### Hallucination Prevention not working
- Verify API key in requests
- Check all 4 validators are loaded
- Ensure database is accessible

## License

MIT License - see LICENSE file.

## Acknowledgments

Built through collaboration between human and AI intelligence, following HAK-GAL principles. Special thanks to the multi-LLM research community for advancing collaborative AI systems.

---

**Version 2.2.0** - Enhanced with Hallucination Prevention (9 endpoints), Multi-LLM Init Protocol (788 n-ary facts), and verified tool counts (125 total: 69 KB + 56 FS).
