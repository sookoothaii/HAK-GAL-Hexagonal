# HAK-GAL Hexagonal

**Advanced Multi-Agent Knowledge System with MCP Integration**

## 🎯 Overview

HAK-GAL Hexagonal is a complete rewrite of the original HAK-GAL-Suite, now featuring:
- Hexagonal Architecture (Ports & Adapters)
- Model Context Protocol (MCP) with 67 tools
- Multi-Agent System (4 adapters)
- Visual Workflow Editor (122 node types)
- SQLite Knowledge Base (6,631 facts)

## 📊 Verified System Stats

| Component | Count | Status |
|-----------|-------|---------|
| MCP Tools | 67 | ✅ Operational |
| Knowledge Facts | 6,631 | ✅ Active |
| Agent Adapters | 4 | ✅ Connected |
| Workflow Nodes | 122 | ✅ Available |

## 🚀 Quick Start

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
# Start MCP Server
python ultimate_mcp/hakgal_mcp_ultimate.py

# Start API Server (separate terminal)
python src_hexagonal/hexagonal_api_enhanced_clean.py

# Start Frontend (separate terminal)
cd frontend
npm run dev
```

## 🛠️ Architecture

### Hexagonal Architecture
```
src_hexagonal/
├── adapters/         # External interfaces
├── core/            # Domain logic
├── application/     # Use cases
├── infrastructure/  # Technical details
└── plugins/         # Future extensions
```

### Multi-Agent System
- **Gemini Adapter**: Google AI integration
- **Claude CLI Adapter**: Anthropic Claude
- **Claude Desktop Adapter**: MCP Protocol
- **Cursor Adapter**: IDE integration

## 📚 Knowledge Base

- **Database**: SQLite with WAL mode
- **Facts**: 6,631 (as of 2025-09-06)
- **Format**: Prolog-style triples
- **Example**: `ConsistsOf(HAK_GAL_System, Hexagonal_Architecture).`

## 🔧 MCP Tools (67 total)

### Categories:
- **Knowledge Base**: ~35 tools
- **File Operations**: 13 tools
- **Database Operations**: 7 tools
- **Multi-Agent**: 1 tool
- **Code Execution**: 1 tool
- **Optional Extensions**: Meta-Tools, Sentry, Nischen

## 🎨 Frontend: WorkflowPro

Visual workflow editor with:
- 122 node types
- Drag-and-drop interface
- Real-time execution
- ReactFlow-based

## 📋 HAK/GAL Constitution

The system follows 8 constitutional articles:
1. Complementary Intelligence
2. Targeted Interrogation
3. External Verification
4. Conscious Boundary-Crossing
5. System Meta-reflection
6. Empirical Validation
7. Conjugated States
8. Principle Collision Protocol

## 🔐 Security

- API Key authentication
- Write token protection
- Audit logging
- Sandboxed code execution

## 🤝 Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

## 📄 License

[License details to be added]

## 🙏 Acknowledgments

Built through collaboration between human and AI intelligence, following HAK-GAL principles.

---

*This is version 2.0 of HAK-GAL, completely rewritten with hexagonal architecture and MCP protocol.*
