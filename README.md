# HAK-GAL Hexagonal

**Advanced Multi-Agent Knowledge System with MCP Integration**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tools](https://img.shields.io/badge/MCP%20Tools-67-orange.svg)](ultimate_mcp/)
[![Facts](https://img.shields.io/badge/Knowledge%20Facts-6631-purple.svg)](hexagonal_kb.db)

## Overview

HAK-GAL Hexagonal is a complete rewrite of the original HAK-GAL-Suite, now featuring:
- **Hexagonal Architecture** (Ports & Adapters)
- **Model Context Protocol (MCP)** with 67 tools
- **Multi-Agent System** (4 adapters)
- **Visual Workflow Editor** (122 node types)
- **SQLite Knowledge Base** (6,631 facts)

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 16+
- Virtual Environment

### Installation

```bash
# Clone repository
git clone https://github.com/sookoothaii/HAK-GAL-Hexagonal.git
cd HAK-GAL-Hexagonal

# Setup Python environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Setup frontend
cd frontend
npm install
```

### Running the System

```bash
# Terminal 1: Start MCP Server
python ultimate_mcp/hakgal_mcp_ultimate.py

# Terminal 2: Start API Server (Port 5002)
python src_hexagonal/hexagonal_api_enhanced_clean.py

# Terminal 3: Start Frontend (Port 5173)
cd frontend
npm run dev
```

## 🛠️ Architecture

### System Components
```
HAK-GAL Hexagonal/
├── ultimate_mcp/        # MCP Server (67 tools)
├── src_hexagonal/       # Hexagonal Backend
│   ├── adapters/        # External interfaces
│   ├── core/           # Domain logic
│   └── application/    # Use cases
├── frontend/           # React + Vite UI
└── workflows/          # Workflow definitions
```

### Multi-Agent System
- **Gemini Adapter**: Google AI integration
- **Claude CLI Adapter**: Anthropic Claude
- **Claude Desktop Adapter**: MCP Protocol
- **Cursor Adapter**: IDE integration

## Knowledge Base

- **Database**: SQLite with WAL mode
- **Facts**: 6,631 (as of 2025-09-06)
- **Format**: Prolog-style triples
- **Example**: `ConsistsOf(HAK_GAL_System, Hexagonal_Architecture).`

## MCP Tools

67 tools across 7 categories:

| Category | Count | Examples |
|----------|-------|----------|
| Knowledge Base | 35 | search_knowledge, add_fact, semantic_similarity |
| File Operations | 13 | read_file, write_file, grep |
| Database Ops | 7 | db_vacuum, db_backup_now |
| Multi-Agent | 1 | delegate_task |
| Code Execution | 1 | execute_code |
| Meta Tools | 4 | consensus_evaluator, bias_detector |
| Optional | 5+ | Sentry, Nischen tools |

## WorkflowPro

Visual workflow editor featuring:
- 122 node types
- Drag-and-drop interface
- Real-time execution
- Complex logic support (branches, loops, error handling)
- Multi-agent orchestration

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

## Security

- API Key authentication
- Write token protection  
- Audit logging
- Sandboxed code execution

## Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

## Performance

- **API Response**: < 100ms (local)
- **Knowledge Search**: < 30ms
- **DB Inserts**: 10,000+/sec
- **Code Execution**: Sandboxed with timeouts

## Roadmap

- [ ] External Integration Plugin System
- [ ] Credential Vault Implementation
- [ ] n8n-style Node Library  
- [ ] Enhanced Data Mapping
- [ ] GraphDB Migration

## Documentation

- [System Architecture](docs/ARCHITECTURE.md)
- [API Documentation](docs/API.md)
- [Workflow Tutorial](PROJECT_HUB/WORKFLOW_TUTORIAL.md)
- [MCP Tools Reference](docs/MCP_TOOLS_REFERENCE.md)

## Acknowledgments

Built through collaboration between human and AI intelligence, following HAK-GAL principles.

---

*Version 2.0 - Complete rewrite with hexagonal architecture and MCP protocol* samui.science.lab 2025
