"""
Hardened AuditLogger - No silent failures, guaranteed persistence
"""

from __future__ import annotations

import json
import hashlib
import threading
import os
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class HardenedAuditLogger:
    """
    Hardened append-only JSONL audit logger with hash chaining.
    NO SILENT FAILURES - crashes the system rather than losing audit data.
    """

    def __init__(self, 
                 project_root: Optional[Path] = None, 
                 filename: str = 'audit_log.jsonl',
                 kill_switch = None) -> None:
        self.project_root = project_root or Path(__file__).resolve().parents[2]
        self.path = self.project_root / filename
        self._last_hash = None
        self._lock = threading.Lock()
        self.kill_switch = kill_switch
        
        # Initialize or load existing chain
        if not self._init_chain():
            error_msg = f"Failed to initialize audit chain at {self.path}"
            logger.critical(error_msg)
            if self.kill_switch:
                self.kill_switch.activate(reason=error_msg, severity="CRITICAL")
            raise RuntimeError(error_msg)
        
        logger.info(f"HardenedAuditLogger initialized: {self.path}")
    
    def _init_chain(self) -> bool:
        """Initialize or load existing hash chain"""
        try:
            if not self.path.exists():
                # Create new audit log
                self.path.parent.mkdir(parents=True, exist_ok=True)
                self._last_hash = hashlib.sha256(b'genesis').hexdigest()
                
                # Write genesis entry
                genesis = {
                    'ts': datetime.now(timezone.utc).isoformat(),
                    'event': 'audit.genesis',
                    'payload': {'message': 'Audit log initialized'},
                    'prev_hash': None,
                    'entry_hash': self._last_hash
                }
                
                with self.path.open('w', encoding='utf-8') as f:
                    f.write(json.dumps(genesis, ensure_ascii=False) + '\n')
                    f.flush()
                    os.fsync(f.fileno())  # Force write to disk
                
                logger.info("Created new audit log with genesis block")
                return True
            
            # Load existing chain
            last_entry = self._get_last_entry()
            if last_entry:
                self._last_hash = last_entry.get('entry_hash')
                if not self._last_hash:
                    logger.error("Last entry missing hash")
                    return False
                
                # Verify chain integrity (last few entries)
                if not self._verify_recent_chain(5):
                    logger.error("Chain integrity check failed")
                    return False
                
                logger.info(f"Loaded existing chain, last_hash={self._last_hash[:8]}...")
                return True
            else:
                logger.error("Existing audit log is empty or corrupted")
                return False
                
        except IOError as e:
            logger.error(f"IO error initializing audit chain: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error initializing audit chain: {e}")
            return False
    
    def _get_last_entry(self) -> Optional[Dict[str, Any]]:
        """Get the last entry from the audit log"""
        try:
            with self.path.open('rb') as f:
                # Seek to end and read backwards
                f.seek(0, 2)
                end = f.tell()
                
                if end == 0:
                    return None
                
                # Read last 4KB or entire file if smaller
                chunk_size = min(4096, end)
                f.seek(max(0, end - chunk_size))
                chunk = f.read()
                
                # Find last complete line
                lines = chunk.splitlines()
                for line in reversed(lines):
                    if line.strip():
                        try:
                            return json.loads(line.decode('utf-8'))
                        except (json.JSONDecodeError, UnicodeDecodeError):
                            continue
                
                return None
                
        except IOError as e:
            logger.error(f"Failed to read last entry: {e}")
            return None
    
    def _verify_recent_chain(self, num_entries: int = 5) -> bool:
        """Verify the integrity of recent entries"""
        try:
            entries = []
            with self.path.open('r', encoding='utf-8') as f:
                # Read last N entries
                for line in f:
                    if line.strip():
                        try:
                            entries.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
            
            if not entries:
                return False
            
            # Check last N entries
            check_count = min(num_entries, len(entries))
            recent = entries[-check_count:]
            
            for i in range(1, len(recent)):
                curr = recent[i]
                prev = recent[i-1]
                
                # Verify hash chain
                if curr.get('prev_hash') != prev.get('entry_hash'):
                    logger.error(f"Chain broken at entry {i}")
                    return False
                
                # Verify entry hash
                expected_hash = self._compute_entry_hash(
                    curr.get('ts'),
                    curr.get('event'),
                    curr.get('payload'),
                    curr.get('prev_hash')
                )
                
                if curr.get('entry_hash') != expected_hash:
                    logger.error(f"Invalid hash at entry {i}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Chain verification failed: {e}")
            return False

    def _compute_entry_hash(self, ts: str, event: str, payload: Dict, prev_hash: str) -> str:
        """Compute hash for an entry"""
        data = {
            'ts': ts,
            'event': event,
            'payload': payload,
            'prev_hash': prev_hash
        }
        payload_bytes = json.dumps(data, sort_keys=True, ensure_ascii=False).encode('utf-8')
        return hashlib.sha256(payload_bytes).hexdigest()

    def log(self, event: str, payload: Dict[str, Any]) -> str:
        """
        Log an entry with guaranteed persistence.
        Returns the entry hash or raises an exception.
        NEVER fails silently.
        """
        if not event:
            raise ValueError("Event cannot be empty")
        
        if not isinstance(payload, dict):
            raise TypeError(f"Payload must be dict, got {type(payload)}")
        
        with self._lock:
            try:
                # Create entry
                ts = datetime.now(timezone.utc).isoformat()
                entry_hash = self._compute_entry_hash(ts, event, payload, self._last_hash)
                
                entry = {
                    'ts': ts,
                    'event': event,
                    'payload': payload,
                    'prev_hash': self._last_hash,
                    'entry_hash': entry_hash
                }
                
                # Persist with guaranteed write
                line = json.dumps(entry, ensure_ascii=False)
                
                with self.path.open('a', encoding='utf-8') as f:
                    f.write(line + '\n')
                    f.flush()
                    # Force write to disk
                    os.fsync(f.fileno())
                
                # Update state only after successful write
                self._last_hash = entry_hash
                
                logger.debug(f"Logged event: {event}, hash={entry_hash[:8]}...")
                return entry_hash
                
            except IOError as e:
                error_msg = f"Critical audit write failure: {e}"
                logger.critical(error_msg)
                
                # Trigger emergency shutdown
                if self.kill_switch:
                    self.kill_switch.activate(
                        reason=error_msg, 
                        severity="CRITICAL"
                    )
                
                # Try to alert monitoring
                try:
                    import sentry_sdk
                    sentry_sdk.capture_message(
                        f"AUDIT FAILURE: {error_msg}", 
                        level="fatal"
                    )
                except ImportError:
                    pass
                
                # Never fail silently
                raise RuntimeError(error_msg) from e
                
            except Exception as e:
                error_msg = f"Unexpected audit failure: {e}"
                logger.critical(error_msg)
                
                if self.kill_switch:
                    self.kill_switch.activate(
                        reason=error_msg, 
                        severity="CRITICAL"
                    )
                
                raise RuntimeError(error_msg) from e
    
    def verify_integrity(self, full_check: bool = False) -> bool:
        """
        Verify the integrity of the audit chain.
        full_check=True checks entire chain (slow for large logs).
        """
        with self._lock:
            try:
                if full_check:
                    logger.info("Starting full chain integrity check...")
                    return self._verify_full_chain()
                else:
                    return self._verify_recent_chain(10)
            except Exception as e:
                logger.error(f"Integrity check failed: {e}")
                return False
    
    def _verify_full_chain(self) -> bool:
        """Verify the entire chain from genesis"""
        try:
            prev_hash = None
            line_num = 0
            
            with self.path.open('r', encoding='utf-8') as f:
                for line in f:
                    line_num += 1
                    
                    if not line.strip():
                        continue
                    
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON at line {line_num}: {e}")
                        return False
                    
                    # Check chain linkage
                    if prev_hash is not None:
                        if entry.get('prev_hash') != prev_hash:
                            logger.error(f"Chain broken at line {line_num}")
                            return False
                    
                    # Verify entry hash
                    expected_hash = self._compute_entry_hash(
                        entry.get('ts'),
                        entry.get('event'),
                        entry.get('payload'),
                        entry.get('prev_hash')
                    )
                    
                    if entry.get('entry_hash') != expected_hash:
                        logger.error(f"Invalid hash at line {line_num}")
                        return False
                    
                    prev_hash = entry.get('entry_hash')
            
            logger.info(f"Full chain verified: {line_num} entries")
            return True
            
        except IOError as e:
            logger.error(f"Failed to read audit log for verification: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get audit log statistics"""
        try:
            line_count = 0
            file_size = self.path.stat().st_size
            
            with self.path.open('r', encoding='utf-8') as f:
                for _ in f:
                    line_count += 1
            
            return {
                'entries': line_count,
                'size_bytes': file_size,
                'path': str(self.path),
                'last_hash': self._last_hash[:8] + '...' if self._last_hash else None,
                'integrity': self.verify_integrity(full_check=False)
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {
                'error': str(e)
            }

# Alias for backwards compatibility
AuditLogger = HardenedAuditLogger