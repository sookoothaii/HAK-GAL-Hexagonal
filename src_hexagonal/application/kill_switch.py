"""
Kill Switch - Emergency shutdown mechanism for critical failures
"""

import os
import sys
import logging
import threading
import signal
import time
from datetime import datetime
from typing import Optional, List, Callable
from pathlib import Path

logger = logging.getLogger(__name__)


class KillSwitch:
    """
    Emergency shutdown mechanism for critical system failures.
    Singleton pattern to ensure only one kill switch exists.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._activated = False
        self._activation_lock = threading.Lock()
        self._shutdown_callbacks: List[Callable] = []
        self._activation_log = Path.cwd() / 'kill_switch_activations.log'
        
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        logger.info("Kill switch initialized")
    
    def _signal_handler(self, signum, frame):
        """Handle system signals"""
        logger.info(f"Received signal {signum}")
        self.activate(
            reason=f"System signal {signum}",
            severity="SIGNAL"
        )
    
    def register_callback(self, callback: Callable):
        """Register a callback to be called on activation"""
        if callable(callback):
            self._shutdown_callbacks.append(callback)
            logger.debug(f"Registered shutdown callback: {callback.__name__}")
    
    def activate(self, reason: str, severity: str = "CRITICAL") -> None:
        """
        Activate the kill switch - initiates emergency shutdown.
        
        Args:
            reason: Description of why kill switch was activated
            severity: Severity level (CRITICAL, ERROR, WARNING, SIGNAL)
        """
        with self._activation_lock:
            if self._activated:
                logger.warning("Kill switch already activated, ignoring duplicate activation")
                return
            
            self._activated = True
            activation_time = datetime.utcnow().isoformat()
            
            # Log to console
            logger.critical(f"""
╔══════════════════════════════════════════════════════════════╗
║                    KILL SWITCH ACTIVATED                     ║
╠══════════════════════════════════════════════════════════════╣
║ Time:     {activation_time:<48}║
║ Severity: {severity:<48}║
║ Reason:   {reason[:48]:<48}║
╚══════════════════════════════════════════════════════════════╝
            """)
            
            # Log to file
            self._log_activation(activation_time, severity, reason)
            
            # Alert monitoring systems
            self._alert_monitoring(reason, severity)
            
            # Execute shutdown callbacks
            self._execute_callbacks()
            
            # Perform emergency data persistence
            self._emergency_persist()
            
            # Determine exit code based on severity
            exit_codes = {
                'CRITICAL': 1,
                'ERROR': 2,
                'WARNING': 3,
                'SIGNAL': 130,
            }
            exit_code = exit_codes.get(severity, 1)
            
            # Give processes time to clean up
            logger.info("Initiating shutdown sequence...")
            time.sleep(2)
            
            # Force exit
            logger.critical(f"Forcing system exit with code {exit_code}")
            os._exit(exit_code)
    
    def _log_activation(self, timestamp: str, severity: str, reason: str):
        """Log activation to persistent file"""
        try:
            with self._activation_log.open('a', encoding='utf-8') as f:
                f.write(f"{timestamp} | {severity} | {reason}\n")
                f.flush()
                os.fsync(f.fileno())
        except Exception as e:
            logger.error(f"Failed to log kill switch activation: {e}")
    
    def _alert_monitoring(self, reason: str, severity: str):
        """Alert external monitoring systems"""
        # Try Sentry
        try:
            import sentry_sdk
            sentry_sdk.capture_message(
                f"KILL SWITCH: {reason}",
                level="fatal" if severity == "CRITICAL" else "error"
            )
            logger.info("Alerted Sentry")
        except ImportError:
            logger.warning("Sentry not available")
        except Exception as e:
            logger.error(f"Failed to alert Sentry: {e}")
        
        # Try system logging
        try:
            if sys.platform != 'win32':
                import syslog
                syslog.syslog(
                    syslog.LOG_CRIT if severity == "CRITICAL" else syslog.LOG_ERR,
                    f"HAK/GAL KILL SWITCH: {reason}"
                )
                logger.info("Logged to syslog")
        except Exception as e:
            logger.error(f"Failed to log to syslog: {e}")
        
        # Windows Event Log
        if sys.platform == 'win32':
            try:
                import win32evtlogutil
                import win32evtlog
                
                win32evtlogutil.ReportEvent(
                    "HAK/GAL",
                    win32evtlog.EVENTLOG_ERROR_TYPE if severity == "CRITICAL" else win32evtlog.EVENTLOG_WARNING_TYPE,
                    eventCategory=1,
                    strings=[f"KILL SWITCH: {reason}"]
                )
                logger.info("Logged to Windows Event Log")
            except ImportError:
                logger.warning("pywin32 not available for Windows Event Log")
            except Exception as e:
                logger.error(f"Failed to log to Windows Event Log: {e}")
    
    def _execute_callbacks(self):
        """Execute registered shutdown callbacks"""
        for callback in self._shutdown_callbacks:
            try:
                logger.info(f"Executing shutdown callback: {callback.__name__}")
                callback()
            except Exception as e:
                logger.error(f"Shutdown callback failed: {e}")
    
    def _emergency_persist(self):
        """Attempt to persist critical data before shutdown"""
        try:
            # Create emergency dump directory
            dump_dir = Path.cwd() / 'emergency_dumps'
            dump_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            dump_file = dump_dir / f'emergency_{timestamp}.json'
            
            # Collect system state
            import json
            state = {
                'timestamp': timestamp,
                'activated': self._activated,
                'callbacks_count': len(self._shutdown_callbacks),
                'process_id': os.getpid(),
                'working_dir': str(Path.cwd()),
            }
            
            with dump_file.open('w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
            
            logger.info(f"Emergency state dumped to {dump_file}")
            
        except Exception as e:
            logger.error(f"Failed to persist emergency data: {e}")
    
    def is_activated(self) -> bool:
        """Check if kill switch has been activated"""
        return self._activated
    
    def test_activation(self, dry_run: bool = True):
        """
        Test kill switch activation without actually shutting down.
        
        Args:
            dry_run: If True, doesn't actually exit the process
        """
        if not dry_run:
            logger.warning("TEST: Kill switch will actually terminate the process!")
            self.activate(reason="Test activation", severity="WARNING")
        else:
            logger.info("TEST: Simulating kill switch activation (dry run)")
            
            # Simulate logging
            timestamp = datetime.utcnow().isoformat()
            logger.info(f"TEST: Would log activation at {timestamp}")
            
            # Simulate callbacks
            for callback in self._shutdown_callbacks:
                logger.info(f"TEST: Would execute callback {callback.__name__}")
            
            logger.info("TEST: Dry run complete - system would have shut down")


# Convenience function for global access
def activate_kill_switch(reason: str, severity: str = "CRITICAL"):
    """Activate the global kill switch"""
    KillSwitch().activate(reason, severity)
