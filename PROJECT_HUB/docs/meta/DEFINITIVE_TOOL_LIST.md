---
title: "Definitive Tool List"
created: "2025-09-15T00:08:01.041612Z"
author: "system-cleanup"
topics: ["meta"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

# HAK-GAL MCP Server - Definitive Tool List v3.1
**Stand:** 2025-08-29  
**Total Tools:** 47 (HAK-GAL namespace)

## Tool Breakdown by Category

### 1. Knowledge Base Core (6 tools)
- `get_facts_count` - Get total fact count
- `search_knowledge` - Search knowledge base
- `add_fact` - Add new fact (requires auth)
- `delete_fact` - Delete fact (requires auth)
- `update_fact` - Update existing fact (requires auth)
- `kb_stats` - Get KB statistics

### 2. Knowledge Base Extended (4 tools)
- `get_recent_facts` - Get recent facts
- `list_recent_facts` - List recent facts with details
- `get_predicates_stats` - Predicate usage statistics
- `get_entities_stats` - Entity frequency statistics

### 3. Knowledge Base Analysis (4 tools)
- `semantic_similarity` - Find semantically similar facts
- `consistency_check` - Check for contradictions
- `validate_facts` - Validate fact syntax
- `analyze_duplicates` - Find duplicate facts

### 4. Knowledge Base Query (4 tools)
- `search_by_predicate` - Search by specific predicate
- `query_related` - Find all facts about entity
- `get_fact_history` - Get audit history for fact
- `get_knowledge_graph` - Export knowledge subgraph

### 5. Knowledge Base Management (4 tools)
- `backup_kb` - Create KB backup (requires auth)
- `restore_kb` - Restore from backup (requires auth)
- `bulk_delete` - Delete multiple facts (requires auth)
- `bulk_translate_predicates` - Translate predicates (requires auth)

### 6. Knowledge Base Statistics (6 tools)
- `export_facts` - Export facts to various formats
- `growth_stats` - KB growth over time
- `health_check` - Comprehensive health status
- `list_audit` - List audit log entries
- `find_isolated_facts` - Find unconnected facts
- `inference_chain` - Build inference chains

### 7. File Core Operations (5 tools)
- `read_file` - Read file content
- `write_file` - Write file (requires auth)
- `list_files` - List files in directory
- `get_file_info` - Get file metadata
- `directory_tree` - Show directory structure

### 8. File Management (5 tools)
- `create_file` - Create new file (requires auth)
- `delete_file` - Delete file (requires auth)
- `move_file` - Move/rename file (requires auth)
- `edit_file` - Edit file content (requires auth)
- `multi_edit` - Multiple edits (requires auth)

### 9. File Search (3 tools)
- `grep` - Search pattern in files
- `find_files` - Find files by pattern
- `search` - Unified search interface

### 10. Project Management (3 tools)
- `project_snapshot` - Create project snapshot (requires auth)
- `project_list_snapshots` - List project snapshots
- `project_hub_digest` - Get project hub summary

### 11. System/Agent (3 tools)
- `delegate_task` - Delegate to other agents
- `execute_code` - Execute code in sandbox
- `get_system_status` - Get system status

## Total Count Verification

| Category | Count |
|----------|-------|
| KB Core | 6 |
| KB Extended | 4 |
| KB Analysis | 4 |
| KB Query | 4 |
| KB Management | 4 |
| KB Statistics | 6 |
| File Core | 5 |
| File Management | 5 |
| File Search | 3 |
| Project | 3 |
| System | 3 |
| **TOTAL** | **47** |

## Additional Tools (Not in HAK-GAL namespace)

These tools may appear in some LLM contexts but are not part of the core HAK-GAL MCP:

### Filesystem Standard Tools (11)
- `Filesystem:read_file`
- `Filesystem:read_multiple_files`
- `Filesystem:write_file`
- `Filesystem:edit_file`
- `Filesystem:create_directory`
- `Filesystem:list_directory`
- `Filesystem:directory_tree`
- `Filesystem:move_file`
- `Filesystem:search_files`
- `Filesystem:get_file_info`
- `Filesystem:list_allowed_directories`

### Other Integration Tools
- Sentry tools (19+)
- Socket:depscore
- artifacts
- repl
- web_search
- web_fetch
- conversation_search
- recent_chats
- end_conversation

## Resolution of Discrepancy

The confusion arose because:
1. **43 tools** - Early documentation (outdated)
2. **44 tools** - Missing 3 tools from count
3. **47 tools** - Correct count for HAK-GAL namespace ✅
4. **80+ tools** - If including all namespaces

## Authoritative Declaration

**The HAK-GAL MCP Server v3.1 provides exactly 47 tools in the `hak-gal:` namespace.**

This is the definitive count that should be used in all documentation and implementations.

---
*Generated: 2025-08-29*  
*Verified by: Direct code analysis and empirical testing*