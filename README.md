# HAK-GAL Hexagonal

**Advanced Multi-Agent Knowledge System with MCP Integration**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![KB Tools](https://img.shields.io/badge/KB%20Tools-68-orange.svg)](ultimate_mcp/)
[![FS Tools](https://img.shields.io/badge/FS%20Tools-20-yellow.svg)](filesystem_mcp/)
[![Total Tools](https://img.shields.io/badge/Total%20Tools-88-purple.svg)](docs/MCP_TOOLS_REFERENCE.md)
[![Facts](https://img.shields.io/badge/Knowledge%20Facts-6631-blue.svg)](https://github.com/sookoothaii/HAK-GAL-Hexagonal/releases/tag/v2.0.0)

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
- Git
- curl or wget

### Installation

```bash
# 1. Clone repository
git clone https://github.com/sookoothaii/HAK-GAL-Hexagonal.git
cd HAK-GAL-Hexagonal

# 2. WICHTIG: Download Knowledge Base (7.1 MB)
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

# Terminal 1: Start MCP KB Server
python ultimate_mcp/hakgal_mcp_ultimate.py

# Terminal 2: Start MCP Filesystem Server (NEW!)
python filesystem_mcp/hak_gal_filesystem.py

# Terminal 3: Start API Server (Port 5002)
python src_hexagonal/hexagonal_api_enhanced_clean.py

# Terminal 4: Start Frontend (Port 5173)
cd frontend
npm run dev
```

Open http://localhost:5173 in your browser.

### Using Both MCP Servers

For maximum functionality, run both MCP servers:
- **KB Server** (`ultimate_mcp`): Knowledge base and AI operations
- **Filesystem Server** (`filesystem_mcp`): Advanced file operations

Configure Claude Desktop to use both servers in `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "hak-gal-kb": {
      "command": "python",
      "args": ["path/to/ultimate_mcp/hakgal_mcp_ultimate.py"]
    },
    "hak-gal-filesystem": {
      "command": "python",
      "args": ["path/to/filesystem_mcp/hak_gal_filesystem.py"]
    }
  }
}
```

## Architecture

### System Components
```
HAK-GAL Hexagonal/
├── ultimate_mcp/        # MCP Server (68 KB tools)
├── filesystem_mcp/      # Filesystem Server (20 tools) - NEW!
├── src_hexagonal/       # Hexagonal Backend
│   ├── adapters/        # External interfaces
│   ├── core/           # Domain logic
│   └── application/    # Use cases
├── frontend/           # React + Vite UI
├── native/             # C++ performance modules
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
- **Size**: 7.1 MB (downloaded separately)

## MCP Tools

**Total: 88 tools** across two specialized servers:

### Knowledge Base Server (`ultimate_mcp`)
68 tools across 7 categories:

| Category | Count | Examples |
|----------|-------|----------|
| Knowledge Base | 35 | search_knowledge, add_fact, semantic_similarity |
| File Operations | 13 | read_file, write_file, grep |
| Database Ops | 7 | db_vacuum, db_backup_now |
| Multi-Agent | 1 | delegate_task |
| Code Execution | 1 | execute_code |
| Meta Tools | 4 | consensus_evaluator, bias_detector |
| Sentry/Nischen | 6 | Optional monitoring tools |

### Filesystem Server (`filesystem_mcp`) - NEW!
20 specialized file operation tools:

| Category | Count | Examples |
|----------|-------|----------|
| Execution | 1 | execute_code (sandboxed) |
| File Operations | 10 | copy_batch, create_directory, move_file |
| Analysis | 3 | file_diff, calculate_hash, tail_file |
| Search & Edit | 5 | grep, find_files, multi_edit |
| Code Tools | 1 | format_code |

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

## Configuration

1. Copy `.env.example` to `.env`
2. Add your API keys:
   - `GEMINI_API_KEY` for Google AI
   - `DEEPSEEK_API_KEY` for DeepSeek
   - Other LLM providers as needed

## Security

- API Key authentication
- Write token protection  
- Audit logging
- Sandboxed code execution
- No network access from sandbox

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Performance

- **API Response**: < 100ms (local)
- **Knowledge Search**: < 30ms
- **DB Inserts**: 10,000+/sec
- **Code Execution**: Sandboxed with timeouts
- **Native C++ modules**: For performance-critical operations

## Roadmap

- [ ] External Integration Plugin System
- [ ] Credential Vault Implementation
- [ ] n8n-style Node Library  
- [ ] Enhanced Data Mapping
- [ ] GraphDB Migration
## Documentation

- [Database Setup](DATABASE_SETUP.md) - Knowledge Base installation
- [System Architecture](docs/ARCHITECTURE.md)
- [API Documentation](docs/API.md)
- [Workflow Tutorial](PROJECT_HUB/WORKFLOW_TUTORIAL.md)
- [MCP Tools Reference](docs/MCP_TOOLS_REFERENCE.md)

## Troubleshooting

### System won't start
- Ensure `hexagonal_kb.db` exists (run `download_kb.bat/sh`)
- Check Python version >= 3.11
- Verify all ports are free (5002, 5173)

### Import errors
- Activate virtual environment
- Run `pip install -r requirements.txt`

### Frontend issues
- Clear browser cache
- Run `npm install` in frontend directory

## License

MIT License - see [LICENSE](LICENSE) file.
## Acknowledgments

Built through collaboration between human and AI intelligence, following HAK-GAL principles.

---

*Version 2.0.0 - Complete rewrite with hexagonal architecture and MCP protocol*
