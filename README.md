# HAK-GAL Hexagonal

**Advanced Multi-Agent Knowledge System with MCP Integration**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![KB Tools](https://img.shields.io/badge/KB%20Tools-64-orange.svg)](ultimate_mcp/)
[![FS Tools](https://img.shields.io/badge/FS%20Tools-55-yellow.svg)](filesystem_mcp/)
[![Total Tools](https://img.shields.io/badge/Total%20Tools-119-purple.svg)](docs/MCP_TOOLS_REFERENCE.md)
[![MCPSuperAssistant](https://img.shields.io/badge/Use%20with-MCPSuperAssistant.ai-brightgreen.svg)](https://mcpsuperassistant.ai)
[![Facts](https://img.shields.io/badge/Knowledge%20Facts-6631-blue.svg)](https://github.com/sookoothaii/HAK-GAL-Hexagonal/releases/tag/v2.0.0)

## Overview

HAK-GAL Hexagonal is a complete rewrite of the original HAK-GAL-Suite, now featuring:
- **Hexagonal Architecture** (Ports & Adapters)
- **Dual MCP Servers** with 119 total tools
  - Knowledge Base Server: 64 tools
  - Filesystem Server: 55 tools (v4.1 with Extended Tools)
- **Browser Integration** via [MCPSuperAssistant.ai](https://mcpsuperassistant.ai)
- **Multi-Agent System** (4 adapters)
- **Visual Workflow Editor** (122 node types)
- **SQLite Knowledge Base** (6,631 facts)

## Quick Start with MCPSuperAssistant.ai (Browser)

The easiest way to use HAK-GAL's MCP servers is through [MCPSuperAssistant.ai](https://mcpsuperassistant.ai):

1. **Start the MCP Proxy for your chosen server:**
   ```bash
   # For Filesystem Server (55 tools)
   npx @srbhptl39/mcp-superassistant-proxy@latest --config ./filesystem-mcp.sse.config.json --outputTransport sse --port 3007
   
   # For KB Server (64 tools)
   npx @srbhptl39/mcp-superassistant-proxy@latest --config ./kb-mcp.sse.config.json --outputTransport sse --port 3008
   
   # Or run both for all 119 tools!
   ```

2. **Open MCPSuperAssistant.ai in your browser**
3. **Add your server(s):**
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

# Terminal 1: Start MCP KB Server (64 tools)
python ultimate_mcp/hakgal_mcp_ultimate.py

# Terminal 2: Start MCP Filesystem Server (55 tools) - v4.1
python filesystem_mcp/hak_gal_filesystem.py

# Terminal 3: Start API Server (Port 5002)
python src_hexagonal/hexagonal_api_enhanced_clean.py

# Terminal 4: Start Frontend (Port 5173)
cd frontend
npm run dev
```

Open http://localhost:5173 in your browser.

### Using Both MCP Servers

You have two powerful MCP servers to choose from or use together:

#### 1. Knowledge Base Server (`ultimate_mcp`) - 64 Tools
- Focus: Knowledge management, semantic search, and AI operations
- Specialties: Facts management, consensus evaluation, multi-agent coordination

#### 2. Filesystem Server (`filesystem_mcp`) - 55 Tools (v4.1)
- Focus: Advanced file operations and development tools
- Specialties: Git operations, package management, build tools, API testing
- NEW: Extended tools for Git, npm/pip/yarn, make/gradle, SQLite, and more

### Browser Usage with MCPSuperAssistant.ai

For the best experience, use [MCPSuperAssistant.ai](https://mcpsuperassistant.ai) in your browser:

1. Configure both servers as SSE endpoints
2. Access all 119 tools directly in the browser
3. No local installation needed for browser usage

Example SSE configuration:
```bash
# For browser usage
npx @srbhptl39/mcp-superassistant-proxy@latest --config ./filesystem-mcp.sse.config.json --outputTransport sse --port 3007
npx @srbhptl39/mcp-superassistant-proxy@latest --config ./kb-mcp.sse.config.json --outputTransport sse --port 3008
```

### Desktop Usage with Claude

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
├── ultimate_mcp/        # KB MCP Server (64 tools)
├── filesystem_mcp/      # Filesystem Server (55 tools) v4.1
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

**Total: 119 tools** across two specialized servers designed for maximum flexibility and redundancy.

### Knowledge Base Server (`ultimate_mcp`) - 64 Tools
Primary focus on knowledge management and AI operations:

| Category | Count | Examples |
|----------|-------|----------|
| Knowledge Base | 35 | search_knowledge, add_fact, semantic_similarity |
| File Operations | 13 | read_file, write_file, grep (redundant for safety) |
| Database Ops | 7 | db_vacuum, db_backup_now, db_checkpoint |
| Multi-Agent | 1 | delegate_task |
| Code Execution | 1 | execute_code |
| Meta Tools | 4 | consensus_evaluator, bias_detector |
| Sentry/Others | 3 | Optional monitoring and utility tools |

### Filesystem Server (`filesystem_mcp`) - 55 Tools (v4.1)
Extended with professional development tools:

| Category | Count | Examples |
|----------|-------|----------|
| Core File Ops | 10 | read_file, write_file, copy_batch, move_file |
| Advanced File Tools | 10 | batch_rename, merge_files, split_file, secure_delete |
| Search & Edit | 5 | grep, find_files, multi_edit |
| Archive & Compression | 4 | archive_create/extract, compress/decompress |
| Git Operations | 6 | git_status, git_commit, git_push, git_pull |
| Package Management | 3 | package_install/list/update (pip, npm, yarn, nuget) |
| Build & Test | 2 | run_build (make, maven, gradle), run_tests |
| Database | 3 | db_connect, db_query, db_schema (SQLite) |
| API Testing | 2 | api_request, api_test_suite |
| Environment Mgmt | 3 | env_create/list/freeze (Python, Conda, Node.js) |
| Analysis & Utils | 7 | file_diff, calculate_hash, format_code, watch_file |

### Redundancy by Design
Some tools (like file operations) are intentionally available in both servers to ensure continued operation if one server fails. This architectural decision provides robustness for critical operations.

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

*Version 2.1.0 - Now with dual MCP servers (119 tools total) and browser support via MCPSuperAssistant.ai*
