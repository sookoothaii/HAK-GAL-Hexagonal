"""
Sentry Integration für Hexagonal Architecture
Nach HAK/GAL Verfassung Artikel 8: Externe Einbettung
"""

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.utils import BadDsn
from typing import Optional
import os

class SentryMonitoring:
    """
    Production Monitoring mit Sentry
    Erfasst Errors, Performance und Custom Events
    """
    
    def __init__(self, dsn: Optional[str] = None):
        # Read DSN, environment and release from parameters or environment variables
        self.dsn = (dsn or os.getenv('SENTRY_DSN') or '').strip()
        self.environment = (
            os.getenv('SENTRY_ENVIRONMENT')
            or os.getenv('SENTRY_ENV')
            or os.getenv('ENVIRONMENT')
            or 'hexagonal-dev'
        )
        self.release = (os.getenv('SENTRY_RELEASE') or '').strip()
        
    def initialize(self, app=None):
        """Initialize Sentry with Flask integration. Never block startup on errors."""
        # Quick DSN validation to avoid BadDsn on obvious placeholders
        invalid_placeholders = {"<dsn>", "dsn", "your_dsn_here", "http://", "https://"}
        if not self.dsn or self.dsn.lower() in invalid_placeholders:
            print("⚠️ Sentry DSN not configured or invalid - monitoring disabled")
            return False

        # Allow runtime tuning via env
        traces_rate_env = os.getenv('SENTRY_TRACES_SAMPLE_RATE')
        profiles_rate_env = os.getenv('SENTRY_PROFILES_SAMPLE_RATE')
        try:
            traces_rate = float(traces_rate_env) if traces_rate_env is not None else 1.0
        except ValueError:
            traces_rate = 1.0
        try:
            profiles_rate = float(profiles_rate_env) if profiles_rate_env is not None else 1.0
        except ValueError:
            profiles_rate = 1.0

        try:
            sentry_sdk.init(
                dsn=self.dsn,
                integrations=[
                    FlaskIntegration(
                        transaction_style='endpoint'
                    ),
                    SqlalchemyIntegration()
                ],
                # Performance Monitoring
                traces_sample_rate=traces_rate,
                profiles_sample_rate=profiles_rate,
                # Release tracking
                release=(self.release if self.release else f"hexagonal@{self._get_version()}"),
                environment=self.environment,
                # Additional options
                attach_stacktrace=True,
                send_default_pii=False,  # GDPR compliance
                # Custom hooks
                before_send=self._before_send,
                before_send_transaction=self._before_transaction
            )
        except BadDsn:
            print("⚠️ Sentry DSN is invalid - monitoring disabled")
            return False
        except Exception as e:
            print(f"⚠️ Sentry initialization failed: {e} - monitoring disabled")
            return False

        print(f"✅ Sentry initialized for environment: {self.environment}")
        return True
    
    def _before_send(self, event, hint):
        """Filter sensitive data before sending"""
        # Remove any API keys from events
        if 'extra' in event:
            for key in list(event['extra'].keys()):
                if 'key' in key.lower() or 'token' in key.lower():
                    event['extra'][key] = '[REDACTED]'
        return event
    
    def _before_transaction(self, event, hint):
        """Enhance transaction data"""
        # Add custom context
        event['contexts']['hexagonal'] = {
            'architecture': 'hexagonal',
            'port': 5001,
            'cuda_available': self._check_cuda()
        }
        return event
    
    def _check_cuda(self) -> bool:
        """Check if CUDA is available"""
        try:
            import torch
            return torch.cuda.is_available()
        except:
            return False
    
    def _get_version(self) -> str:
        """Get application version"""
        try:
            with open('VERSION', 'r') as f:
                return f.read().strip()
        except:
            return '1.0.0'
    
    @staticmethod
    def capture_fact_added(fact_statement: str, success: bool):
        """Custom event for fact additions"""
        with sentry_sdk.push_scope() as scope:
            scope.set_tag("operation", "fact_add")
            scope.set_extra("statement", fact_statement[:100])  # Truncate
            scope.set_extra("success", success)
            
            if success:
                sentry_sdk.capture_message(
                    "Fact added successfully",
                    level="info"
                )
            else:
                sentry_sdk.capture_message(
                    "Failed to add fact",
                    level="warning"
                )
    
    @staticmethod
    def capture_reasoning_performance(query: str, confidence: float, duration_ms: float):
        """Track reasoning performance"""
        with sentry_sdk.start_transaction(
            op="reasoning",
            name="HRM Reasoning"
        ) as transaction:
            transaction.set_tag("query_type", query.split('(')[0] if '(' in query else 'unknown')
            transaction.set_data("confidence", confidence)
            transaction.set_data("duration_ms", duration_ms)
            
            # Performance threshold alerts
            if duration_ms > 100:
                sentry_sdk.capture_message(
                    f"Slow reasoning: {duration_ms}ms",
                    level="warning"
                )
    
    @staticmethod
    def monitor_cuda_memory():
        """Monitor CUDA memory usage"""
        try:
            import torch
            if torch.cuda.is_available():
                allocated = torch.cuda.memory_allocated() / 1024**3  # GB
                reserved = torch.cuda.memory_reserved() / 1024**3
                
                with sentry_sdk.push_scope() as scope:
                    scope.set_context("cuda", {
                        "allocated_gb": allocated,
                        "reserved_gb": reserved,
                        "device": torch.cuda.get_device_name()
                    })
                    
                    if allocated > 8:  # Alert if > 8GB
                        sentry_sdk.capture_message(
                            f"High CUDA memory usage: {allocated:.2f}GB",
                            level="warning"
                        )
        except Exception as e:
            sentry_sdk.capture_exception(e)

# Integration in hexagonal_api.py:
"""
from infrastructure.sentry_monitoring import SentryMonitoring

# In __init__:
self.monitoring = SentryMonitoring()
self.monitoring.initialize(self.app)

# In add_fact endpoint:
SentryMonitoring.capture_fact_added(statement, success)

# In reason endpoint:
import time
start = time.time()
result = self.reasoning_service.reason(query)
duration_ms = (time.time() - start) * 1000
SentryMonitoring.capture_reasoning_performance(query, result.confidence, duration_ms)
"""
