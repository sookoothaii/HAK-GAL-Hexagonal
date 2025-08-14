# Bulk Translate Predicates – Controlled Migration Playbook

This playbook describes a safe, reproducible procedure to migrate predicate names in the knowledge base using the MCP tool `bulk_translate_predicates`. It adheres to HAK/GAL principles: strictly empirical, auditable, and reversible.

---

## 1) Objectives

- Migrate selected predicates (e.g., `HatZweck` → `HasPurpose`, `HatTeil` → `HasPart`).
- Guarantee safety via dry-run, snapshots/backups, and audit logging.
- Enable large-scale changes in controlled batches (resume, limit by changes, offsets).

---

## 2) Preconditions

- Writes enabled: `HAKGAL_WRITE_ENABLED=true` (and optional `HAKGAL_WRITE_TOKEN`).
- MCP Server running (hak-gal) with tool available.
- Project-Hub path set: `HAKGAL_HUB_PATH = D:\MCP Mods\HAK_GAL_HEXAGONAL\PROJECT_HUB`.
- Recommended: Ensure free disk space for backups and temporary files.

---

## 3) Parameters (reference)

- `mapping` (required): JSON object `{ oldPredicate: newPredicate, ... }`.
- `predicates` (optional): allowlist to restrict which predicates are considered.
- `exclude_predicates` (optional): blocklist of predicates to skip even if in mapping.
- `dry_run` (bool, default true): simulate without writing.
- `limit` (int, default 0): with `limit_mode='lines'`, process up to N lines (0 = all).
- `limit_mode` ('lines'|'changes', default 'lines'): interpret `limit` as line-count or number of actual changes.
- `start_offset` (int, default 0): skip first N lines, for resume.
- `sample_strategy` ('head'|'tail'|'stratified', dry-run only): sampling strategy.
- `report_path` (string): optional path to write a summary report (md/json).
- `auth_token` (string): required if `dry_run=false` and a token gate is configured (implicitly accepted locally per server policy).

---

## 4) Quick Start (safe)

1) Dry-run (representative sample):
```json
{
  "method": "tools/call",
  "params": {
    "name": "bulk_translate_predicates",
    "arguments": {
      "mapping": { "HatZweck": "HasPurpose", "HatTeil": "HasPart" },
      "predicates": ["HatZweck","HatTeil"],
      "exclude_predicates": [],
      "dry_run": true,
      "limit": 1000,
      "sample_strategy": "stratified",
      "report_path": "D:/MCP Mods/HAK_GAL_HEXAGONAL/PROJECT_HUB/reports/translate_dryrun.md"
    }
  },
  "id": 1,
  "jsonrpc": "2.0"
}
```

2) Create snapshot (immutable handover before changes):
- Use MCP tool `project_snapshot` with a descriptive title/description.

3) Live batch (changes-capped, safe rollback via snapshot):
```json
{
  "method": "tools/call",
  "params": {
    "name": "bulk_translate_predicates",
    "arguments": {
      "mapping": { "HatZweck": "HasPurpose" },
      "predicates": ["HatZweck"],
      "dry_run": false,
      "limit_mode": "changes",
      "limit": 200,
      "auth_token": ""
    }
  },
  "id": 2,
  "jsonrpc": "2.0"
}
```

4) Validate & Audit:
- Run `validate_facts`, `analyze_duplicates`, `consistency_check`.
- Inspect `mcp_write_audit.log` for the last entries.

---

## 5) Staged Migration Plan (recommended)

### Stage A – Assessment
- Dry-run with stratified sampling (e.g., `limit=2000`, `sample_strategy='stratified'`).
- Review per-predicate change counts and 5–10 example rewrites in the output/report.
- If needed, add `exclude_predicates` to block terms not ready for migration.

### Stage B – Initial Production Batches
- Create snapshot via `project_snapshot` (mandatory for rollback).
- Execute limited changes with `limit_mode='changes'` (e.g., 200–500 changes per batch).
- After each batch:
  - Validate tools: `validate_facts`, `consistency_check`.
  - Spot-check via search (e.g., `search_by_predicate` for old/new names).
  - Confirm audit entries were written.

### Stage C – Resume and Complete
- Use `start_offset` only if you operate in `limit_mode='lines'` across large files and need deterministic resumption.
- For `limit_mode='changes'`, run sequential batches until counts for targeted predicates approach zero.
- Finish with a final snapshot documenting the result (title: “Predicate Migration Completed”).

---

## 6) Tailored Scenarios

- Allowlist-only:
```json
{
  "name":"bulk_translate_predicates",
  "arguments": {
    "mapping": { "HatTeil": "HasPart" },
    "predicates": ["HatTeil"],
    "dry_run": false,
    "limit_mode": "changes",
    "limit": 300
  }
}
```

- Exclude specific predicates while translating others:
```json
{
  "name":"bulk_translate_predicates",
  "arguments": {
    "mapping": { "HatZweck": "HasPurpose", "HatTeil": "HasPart" },
    "exclude_predicates": ["HatTeil"],
    "dry_run": true,
    "limit": 1500,
    "sample_strategy": "stratified"
  }
}
```

- Resume with line offset (when using line-based limits):
```json
{
  "name":"bulk_translate_predicates",
  "arguments": {
    "mapping": { "HatZweck": "HasPurpose" },
    "dry_run": false,
    "limit_mode": "lines",
    "limit": 100000,
    "start_offset": 100000
  }
}
```

- Tail sampling (dry-run window at file end):
```json
{
  "name":"bulk_translate_predicates",
  "arguments": {
    "mapping": { "HatTeil": "HasPart" },
    "dry_run": true,
    "limit": 200,
    "sample_strategy": "tail"
  }
}
```

---

## 7) Safety, Audit & Rollback

- Always snapshot before first live batch.
- Audit: every live run appends JSON lines to `mcp_write_audit.log`:
  - action: `bulk_translate_predicates`
  - payload: mapping, allow/exclude lists, checked/changed counts, per-predicate stats
- Rollback options:
  - Restore snapshot of KB (via `restore_kb` or using the snapshot created by `project_snapshot`).
  - If backups are enabled elsewhere, use `backup_kb`/`restore_kb` identifiers.

---

## 8) Verification Checklist (each batch)

- [ ] Changes summary matches expectation (counts per predicate).
- [ ] `validate_facts` returns OK (or acceptable residual warnings).
- [ ] `consistency_check` does not introduce contradictions.
- [ ] Spot-check old vs new predicates with `search_by_predicate`.
- [ ] Audit file updated and contains accurate metadata.

---

## 9) Known Considerations

- Distribution of predicates may be non-uniform across the file; use `stratified` or `tail` dry-run to sample later segments.
- `limit_mode='changes'` is ideal for precise batch sizes, but does not give a deterministic file position; rely on audit counts.
- When combining `predicates` and `exclude_predicates`, exclusion takes precedence.

---

## 10) Example Mappings (common)

```json
{
  "HatZweck": "HasPurpose",
  "HatTeil": "HasPart",
  "IstTeilVon": "PartOf",
  "IstEin": "IsA"
}
```

Use allow/exclude lists to introduce mappings in stages (e.g., migrate `HatZweck` first, then `HatTeil`).

---

## 11) Appendix: Minimal Troubleshooting

- Tool returns no changes:
  - Check that `mapping` keys match current predicate names exactly.
  - Ensure allow/exclude lists are not blocking your targets.
  - Increase `limit` or adjust `sample_strategy` for dry-run.
- Report file not written:
  - Create the parent directory prior to run; confirm absolute path and permissions.
- Performance:
  - Prefer `limit_mode='changes'` with moderate `limit` (e.g., 200–500) for predictable batches.

---

Author: HAK/GAL Engineering
Last updated: <set on use>

