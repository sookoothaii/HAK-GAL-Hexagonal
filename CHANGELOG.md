# Changelog

All notable changes to HAK-GAL Hexagonal will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-09-06

### Added
- Complete rewrite with hexagonal architecture
- Model Context Protocol (MCP) server with 67 tools
- Multi-agent system with 4 adapters:
  - Gemini Adapter (Google AI)
  - Claude CLI Adapter
  - Claude Desktop Adapter
  - Cursor Adapter
- WorkflowPro visual editor with 122 node types
- Real-time WebSocket communication
- Execute code sandbox
- SQLite knowledge base with 6,631 facts
- HAK-GAL Constitution with 8 articles
- Comprehensive test suite
- CI/CD with GitHub Actions

### Changed
- Migrated from monolithic to hexagonal architecture
- Replaced JSON with SQLite for knowledge base
- Improved performance (10,000+ inserts/sec)
- Enhanced security with sandboxed execution

### Technical Details
- Python 3.11+ required
- React + Vite frontend
- Flask + SocketIO backend
- WAL mode for database

## [1.0.0] - 2025-08-14 (Legacy)

Initial version of HAK-GAL-Suite (deprecated)
