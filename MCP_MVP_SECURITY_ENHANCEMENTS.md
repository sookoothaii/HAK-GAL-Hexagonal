# HAK-GAL MCP MVP Security & Quality Enhancements

**Document ID:** HAK-GAL-MCP-MVP-ENHANCEMENTS-20250813  
**Status:** Implementation Critical - GPT-5 Validated Improvements  
**Base Document:** MCP_MVP_IMPLEMENTATION_PLAN.md  
**Priority:** MANDATORY - Must-Haves before Phase 2  

---

## Executive Summary

Following GPT-5's detailed validation of our MVP plan, this document addresses critical security, reliability, and quality enhancements that must be implemented as part of the MVP foundation. These are not optional improvements - they are **mandatory requirements** for a production-ready MCP integration.

**GPT-5's Assessment:** ✅ "Konzeptionell stark und umsetzbar" with specific technical enhancements required.

---

## Critical Enhancement Areas (GPT-5 Priority)

### 🔐 **1. Enhanced Authentication & Secrets Management**

#### **Current State:** Basic JWT tokens, .env file secrets
#### **GPT-5 Requirements:** JWT rotation, secret store integration, audit trails

#### **Implementation:**
```python
# src_hexagonal/infrastructure/mcp/security/enhanced_auth.py
class EnhancedAuthenticationManager:
    """
    Production-grade auth following GPT-5 security recommendations
    Constitutional Artikel 8: External constraint compliance with strong security
    """
    
    def __init__(self):
        # GPT-5: Secret Store integration (not .env)
        self.secret_store = self.init_secret_store()
        
        # GPT-5: JWT rotation capability
        self.jwt_rotator = JWTRotationManager(
            rotation_interval_hours=6,  # Rotate every 6 hours
            overlap_period_minutes=30   # Allow old tokens for 30 min
        )
        
        # GPT-5: Audit secret access
        self.secret_audit_logger = SecretAccessAuditLogger()
        
    def init_secret_store(self) -> SecretStore:
        """Initialize secure secret storage (Windows Vault/Linux Keyring)"""
        
        if os.name == 'nt':  # Windows
            return WindowsCredentialStore()
        else:  # Linux/Mac
            return SystemKeyringStore()
            
    async def authenticate_with_rotation(self, token: str, client_id: str) -> AuthResult:
        """Enhanced auth with automatic token rotation (Artikel 8: External constraints)"""
        
        # GPT-5: Check both current and previous token generation
        current_valid = await self.validate_jwt_token(token, self.jwt_rotator.current_key)
        
        if not current_valid:
            # Try previous key during rotation overlap
            previous_valid = await self.validate_jwt_token(token, self.jwt_rotator.previous_key)
            
            if not previous_valid:
                await self.secret_audit_logger.log_auth_failure(client_id, token[:8])
                return AuthResult(success=False, reason="invalid_token")
                
            # Valid with old key - client should rotate
            await self.notify_client_token_rotation(client_id)
            
        # GPT-5: Audit successful secret access
        await self.secret_audit_logger.log_secret_access(client_id, "mcp_auth_success")
        
        return AuthResult(success=True, client_id=client_id, 
                         should_rotate=not current_valid)
```

#### **Secret Store Configuration:**
```python
class WindowsCredentialStore:
    """Windows Credential Manager integration"""
    
    def get_secret(self, key: str) -> str:
        """Retrieve secret from Windows Credential Manager"""
        import keyring
        secret = keyring.get_password("HAK_GAL_MCP", key)
        
        # GPT-5: Audit secret retrieval
        self.audit_logger.log_secret_retrieval(key, success=secret is not None)
        
        if not secret:
            raise SecretNotFoundError(f"Secret {key} not found in credential store")
            
        return secret
        
    def set_secret(self, key: str, value: str):
        """Store secret in Windows Credential Manager"""
        import keyring
        keyring.set_password("HAK_GAL_MCP", key, value)
        self.audit_logger.log_secret_storage(key)
```

### ⚡ **2. Enhanced Rate Limiting & Circuit Breakers**

#### **Current State:** Simple per-client rate limiting
#### **GPT-5 Requirements:** Per-tool/client separation, circuit breaker strategies

#### **Implementation:**
```python
# src_hexagonal/infrastructure/mcp/security/enhanced_rate_limiting.py
class AdvancedRateLimiter:
    """
    GPT-5 recommended: Granular rate limiting with circuit breakers
    Constitutional Artikel 8: External constraint compliance
    """
    
    def __init__(self):
        # GPT-5: Per-tool, per-client rate limits
        self.rate_limits = {
            "query_knowledge_base": {"claude": 30, "cursor": 20, "default": 10},
            "neural_reasoning": {"claude": 10, "cursor": 8, "default": 5},
            "get_system_metrics": {"claude": 60, "cursor": 60, "default": 30}
        }
        
        # GPT-5: Circuit breaker states per tool
        self.circuit_breakers = {
            tool: CircuitBreaker(
                failure_threshold=5,
                recovery_timeout=60,
                half_open_max_calls=3
            ) for tool in self.rate_limits.keys()
        }
        
        self.usage_tracker = UsageTracker()
        
    async def check_rate_limit(self, tool: str, client_id: str) -> RateLimitResult:
        """GPT-5: Granular rate limiting with circuit breaker"""
        
        # Check circuit breaker state first
        circuit_breaker = self.circuit_breakers[tool]
        
        if circuit_breaker.state == CircuitState.OPEN:
            return RateLimitResult(
                allowed=False, 
                reason="circuit_breaker_open",
                retry_after=circuit_breaker.next_attempt_time
            )
            
        # Get client-specific or default limit
        client_type = self.get_client_type(client_id)
        limit = self.rate_limits[tool].get(client_type, self.rate_limits[tool]["default"])
        
        # Check current usage
        current_usage = await self.usage_tracker.get_usage(tool, client_id, window_minutes=1)
        
        if current_usage >= limit:
            # GPT-5: Record rate limit hit for circuit breaker
            await circuit_breaker.record_failure()
            
            return RateLimitResult(
                allowed=False,
                reason="rate_limit_exceeded", 
                current_usage=current_usage,
                limit=limit,
                retry_after=60 - (time.time() % 60)  # Next minute window
            )
            
        # GPT-5: Record successful usage
        await circuit_breaker.record_success()
        await self.usage_tracker.record_usage(tool, client_id)
        
        return RateLimitResult(allowed=True, remaining=limit - current_usage - 1)
```

#### **Circuit Breaker Implementation:**
```python
class CircuitBreaker:
    """GPT-5: Circuit breaker with Open→Half-Open→Closed states"""
    
    def __init__(self, failure_threshold: int, recovery_timeout: int, half_open_max_calls: int):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.half_open_calls = 0
        
    async def record_failure(self):
        """Record failure and potentially open circuit"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            await self.notify_circuit_opened()
            
    async def record_success(self):
        """Record success and potentially close circuit"""
        if self.state == CircuitState.HALF_OPEN:
            self.half_open_calls += 1
            
            if self.half_open_calls >= self.half_open_max_calls:
                # Successful recovery
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.half_open_calls = 0
                await self.notify_circuit_closed()
                
        elif self.state == CircuitState.CLOSED:
            # Reset failure count on success
            self.failure_count = max(0, self.failure_count - 1)
            
    @property
    def next_attempt_time(self) -> float:
        """When circuit will move from OPEN to HALF_OPEN"""
        if self.state == CircuitState.OPEN and self.last_failure_time:
            return self.last_failure_time + self.recovery_timeout
        return 0
```

### 🎯 **3. Enhanced Testing & Schema Validation**

#### **Current State:** Basic equivalence testing
#### **GPT-5 Requirements:** Schema equivalence, deterministic fixtures

#### **Implementation:**
```python
# tests/mcp/enhanced_validation_tests.py
class EnhancedMCPValidationTests:
    """
    GPT-5 recommended: Comprehensive equivalence and schema testing
    Constitutional Artikel 6: Rigorous empirical validation
    """
    
    def __init__(self):
        # GPT-5: Deterministic test fixtures
        self.test_fixtures = self.load_deterministic_fixtures()
        
        # GPT-5: JSON Schema validation
        self.schema_validator = MCPSchemaValidator()
        
    def load_deterministic_fixtures(self) -> Dict[str, List[TestCase]]:
        """GPT-5: Stable, deterministic test queries"""
        
        return {
            "knowledge_queries": [
                TestCase(
                    query="hexagonal architecture",
                    expected_min_results=3,
                    expected_confidence_range=(0.7, 1.0),
                    deterministic_seed=12345
                ),
                TestCase(
                    query="neural reasoning systems", 
                    expected_min_results=2,
                    expected_confidence_range=(0.6, 1.0),
                    deterministic_seed=67890
                )
            ],
            "reasoning_queries": [
                TestCase(
                    query="Analyze the benefits of modular architecture",
                    expected_min_confidence=0.5,
                    expected_response_structure=["analysis", "benefits", "conclusions"],
                    deterministic_seed=11111
                )
            ]
        }
        
    async def test_schema_equivalence(self):
        """GPT-5: Verify response schema equivalence between Direct API and MCP"""
        
        for category, test_cases in self.test_fixtures.items():
            for test_case in test_cases:
                # Set deterministic seed for reproducible results
                await self.set_deterministic_seed(test_case.deterministic_seed)
                
                # Direct API call
                direct_response = await self.call_direct_api(test_case)
                
                # MCP call  
                mcp_response = await self.call_mcp_tool(test_case)
                
                # GPT-5: Schema structure validation
                direct_schema = self.extract_schema(direct_response)
                mcp_schema = self.extract_schema(mcp_response["results"])
                
                assert direct_schema == mcp_schema, f"Schema mismatch for {test_case.query}"
                
                # GPT-5: Field type validation
                await self.validate_field_types(direct_response, mcp_response["results"])
                
                # GPT-5: Value range validation
                await self.validate_value_ranges(direct_response, mcp_response["results"], test_case)
                
    async def validate_field_types(self, direct_result: Dict, mcp_result: Dict):
        """Ensure field types match exactly between API responses"""
        
        for field_path, direct_value in self.flatten_dict(direct_result).items():
            mcp_value = self.get_nested_value(mcp_result, field_path)
            
            assert type(direct_value) == type(mcp_value), \
                f"Type mismatch at {field_path}: {type(direct_value)} vs {type(mcp_value)}"
                
    async def validate_value_ranges(self, direct_result: Dict, mcp_result: Dict, test_case: TestCase):
        """GPT-5: Validate confidence scores and other numeric ranges"""
        
        if "confidence" in direct_result and "confidence" in mcp_result:
            direct_conf = direct_result["confidence"]
            mcp_conf = mcp_result["confidence"]
            
            # GPT-5: Confidence should be within 5% (stricter than original plan)
            conf_diff = abs(direct_conf - mcp_conf)
            assert conf_diff < 0.05, f"Confidence variance too high: {conf_diff}"
            
            # Validate against expected range
            assert test_case.expected_confidence_range[0] <= direct_conf <= test_case.expected_confidence_range[1]
            assert test_case.expected_confidence_range[0] <= mcp_conf <= test_case.expected_confidence_range[1]
```

#### **JSON Schema Validation:**
```python
class MCPSchemaValidator:
    """GPT-5: JSON Schema validation for all MCP tools"""
    
    def __init__(self):
        self.schemas = self.load_tool_schemas()
        
    def load_tool_schemas(self) -> Dict[str, Dict]:
        """Load JSON schemas for all MCP tools"""
        
        return {
            "query_knowledge_base": {
                "type": "object",
                "required": ["results", "source", "timestamp", "article_compliance"],
                "properties": {
                    "results": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["fact", "confidence", "source"],
                            "properties": {
                                "fact": {"type": "string", "minLength": 1},
                                "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                                "source": {"type": "string"}
                            }
                        }
                    },
                    "source": {"type": "string", "enum": ["verified_kb_database"]},
                    "timestamp": {"type": "string", "format": "date-time"},
                    "article_compliance": {"type": "string", "enum": ["verified_real_data"]}
                }
            },
            "neural_reasoning_read_only": {
                "type": "object",
                "required": ["reasoning_result", "resource_usage", "article_3_compliance"],
                "properties": {
                    "reasoning_result": {
                        "type": "object",
                        "required": ["conclusion", "confidence", "reasoning_steps"],
                        "properties": {
                            "conclusion": {"type": "string"},
                            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                            "reasoning_steps": {"type": "array", "items": {"type": "string"}}
                        }
                    }
                }
            }
        }
        
    def validate_response(self, tool_name: str, response: Dict) -> ValidationResult:
        """Validate MCP tool response against JSON schema"""
        
        if tool_name not in self.schemas:
            return ValidationResult(valid=False, error=f"No schema defined for tool {tool_name}")
            
        try:
            jsonschema.validate(response, self.schemas[tool_name])
            return ValidationResult(valid=True)
        except jsonschema.ValidationError as e:
            return ValidationResult(valid=False, error=str(e), schema_path=e.absolute_path)
```

### 📊 **4. Enhanced Error Handling & Observability**

#### **Current State:** Basic error responses
#### **GPT-5 Requirements:** Error taxonomy, correlation IDs, PII sanitizing

#### **Implementation:**
```python
# src_hexagonal/infrastructure/mcp/observability/enhanced_error_handling.py
class EnhancedErrorHandler:
    """
    GPT-5 recommended: Unified error taxonomy with actionable hints
    Constitutional Artikel 5: System-Metareflexion error reporting
    """
    
    # GPT-5: Standardized error codes and HTTP status mapping
    ERROR_TAXONOMY = {
        "AUTH_INVALID_TOKEN": {
            "http_status": 401,
            "category": "authentication",
            "severity": "high",
            "actionable_hint": "Token expired or invalid. Request new token from administrator.",
            "user_message": "Authentication failed. Please check your credentials."
        },
        "RATE_LIMIT_EXCEEDED": {
            "http_status": 429,
            "category": "rate_limiting",
            "severity": "medium", 
            "actionable_hint": "Reduce request frequency or upgrade to higher tier.",
            "user_message": "Too many requests. Please wait {retry_after} seconds."
        },
        "RESOURCE_BUDGET_EXCEEDED": {
            "http_status": 503,
            "category": "resource_management",
            "severity": "high",
            "actionable_hint": "Daily GPU/token budget exhausted. Resets at midnight UTC.",
            "user_message": "Resource quota exceeded. Service will resume tomorrow."
        },
        "CIRCUIT_BREAKER_OPEN": {
            "http_status": 503,
            "category": "system_protection",
            "severity": "high",
            "actionable_hint": "System overloaded. Automatic recovery in {recovery_time} seconds.",
            "user_message": "Service temporarily unavailable. Retrying automatically."
        },
        "VALIDATION_SCHEMA_ERROR": {
            "http_status": 422,
            "category": "input_validation",
            "severity": "medium",
            "actionable_hint": "Check input format against tool schema documentation.",
            "user_message": "Invalid input format. Please check your request parameters."
        },
        "CONSTITUTIONAL_VIOLATION": {
            "http_status": 503,
            "category": "compliance",
            "severity": "critical",
            "actionable_hint": "Operation blocked by constitutional compliance. Contact administrator.",
            "user_message": "Operation not permitted by system policies."
        }
    }
    
    def __init__(self):
        self.correlation_id_generator = CorrelationIDGenerator()
        self.pii_sanitizer = PIISanitizer()
        self.error_logger = EnhancedErrorLogger()
        
    async def handle_error(self, error: Exception, context: Dict) -> ErrorResponse:
        """GPT-5: Standardized error handling with correlation tracking"""
        
        # Generate correlation ID for tracking
        correlation_id = self.correlation_id_generator.generate()
        
        # Determine error code
        error_code = self.classify_error(error)
        error_config = self.ERROR_TAXONOMY[error_code]
        
        # GPT-5: Sanitize PII from context
        sanitized_context = await self.pii_sanitizer.sanitize(context)
        
        # Create standardized error response
        error_response = ErrorResponse(
            error_code=error_code,
            http_status=error_config["http_status"],
            category=error_config["category"],
            severity=error_config["severity"],
            user_message=error_config["user_message"].format(**context),
            actionable_hint=error_config["actionable_hint"].format(**context),
            correlation_id=correlation_id,
            timestamp=datetime.utcnow().isoformat(),
            article_4_compliance="transparent_error_reporting"
        )
        
        # GPT-5: Log with correlation ID and sanitized context
        await self.error_logger.log_error(
            error_response=error_response,
            original_error=error,
            sanitized_context=sanitized_context,
            correlation_id=correlation_id
        )
        
        return error_response
```

#### **PII Sanitization:**
```python
class PIISanitizer:
    """GPT-5: Remove PII from logs and error messages"""
    
    def __init__(self):
        # Common PII patterns
        self.pii_patterns = [
            (r'\b\d{3}-\d{2}-\d{4}\b', '[SSN_REDACTED]'),  # SSN
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_REDACTED]'),  # Email
            (r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[CARD_REDACTED]'),  # Credit card
            (r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b', '[PHONE_REDACTED]'),  # Phone
            (r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[IP_REDACTED]'),  # IP Address
        ]
        
    async def sanitize(self, data: Any) -> Any:
        """Recursively sanitize PII from data structures"""
        
        if isinstance(data, str):
            return self.sanitize_string(data)
        elif isinstance(data, dict):
            return {k: await self.sanitize(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [await self.sanitize(item) for item in data]
        else:
            return data
            
    def sanitize_string(self, text: str) -> str:
        """Apply PII patterns to sanitize string"""
        
        for pattern, replacement in self.pii_patterns:
            text = re.sub(pattern, replacement, text)
            
        return text
```

### 🔧 **5. Transport Selection & Security**

#### **Current State:** Basic STDIO and HTTP transports
#### **GPT-5 Requirements:** Selection criteria, TLS for production

#### **Implementation:**
```python
# src_hexagonal/infrastructure/mcp/transports/enhanced_transport_manager.py
class EnhancedTransportManager:
    """
    GPT-5 recommended: Transport selection with security criteria
    Constitutional Artikel 8: External constraint compliance for secure communications
    """
    
    TRANSPORT_CRITERIA = {
        "stdio": {
            "use_cases": ["local_development", "claude_code", "trusted_local_clients"],
            "security_level": "high",  # Process isolation
            "latency": "ultra_low",
            "authentication": "process_based",
            "encryption": "not_needed"  # Local process communication
        },
        "http": {
            "use_cases": ["remote_clients", "cursor", "web_interfaces", "distributed_ai"],
            "security_level": "configurable",
            "latency": "low_to_medium", 
            "authentication": "token_based",
            "encryption": "tls_required"  # Network communication
        },
        "websocket": {
            "use_cases": ["real_time_collaboration", "streaming_responses"],
            "security_level": "configurable",
            "latency": "very_low",
            "authentication": "token_based",
            "encryption": "tls_required"
        }
    }
    
    def select_transport(self, client_type: str, environment: str) -> str:
        """GPT-5: Intelligent transport selection based on criteria"""
        
        if environment == "production":
            # Production: Always use encrypted transports
            if client_type in ["cursor", "web_client", "remote_ai"]:
                return "https"  # HTTP with mandatory TLS
            elif client_type == "claude_code" and self.is_local_client():
                return "stdio"  # Local process, secure by isolation
            else:
                return "wss"    # WebSocket with TLS
                
        elif environment == "development":
            # Development: Prioritize convenience but maintain security
            if client_type == "claude_code":
                return "stdio"
            else:
                return "http"   # Plain HTTP acceptable for dev
                
    async def create_secure_transport(self, transport_type: str, config: Dict) -> Transport:
        """Create transport with appropriate security configuration"""
        
        if transport_type == "https":
            # GPT-5: Mandatory TLS for production HTTP
            return HTTPSTransport(
                host=config.get("host", "0.0.0.0"),
                port=config.get("port", 5002),
                tls_config=TLSConfig(
                    cert_file=config["tls_cert_path"],
                    key_file=config["tls_key_path"],
                    ca_file=config.get("tls_ca_path"),  # For mTLS if needed
                    verify_client=config.get("mutual_tls", False)
                ),
                auth_required=True,
                rate_limiting=True
            )
            
        elif transport_type == "stdio":
            return STDIOTransport(
                process_isolation=True,
                resource_limits=ResourceLimits(
                    max_memory_mb=512,
                    max_cpu_percent=50
                )
            )
            
        elif transport_type == "wss":
            return WebSocketSecureTransport(
                host=config.get("host", "0.0.0.0"),
                port=config.get("port", 5003),
                tls_config=TLSConfig(
                    cert_file=config["tls_cert_path"],
                    key_file=config["tls_key_path"]
                ),
                auth_required=True,
                heartbeat_interval=30
            )
```

---

## Implementation Checklist (Quality Gates Enhanced)

### **Gate 1: Enhanced Security Foundation** ✅
- [ ] **JWT Rotation:** 6-hour token rotation with 30-minute overlap
- [ ] **Secret Store:** Windows Credential Manager / Linux Keyring integration
- [ ] **Audit Trails:** All secret access logged with correlation IDs
- [ ] **Per-Tool Rate Limits:** Separate limits for query_kb, reasoning, metrics
- [ ] **Circuit Breakers:** Open→Half-Open→Closed state machine implemented
- [ ] **PII Sanitization:** All logs and errors sanitized for privacy

### **Gate 2: Schema & Validation** ✅
- [ ] **JSON Schemas:** All MCP tools have formal schemas
- [ ] **Schema Validation:** Request/response validation enforced
- [ ] **Deterministic Tests:** Stable fixtures with reproducible results
- [ ] **Field Type Validation:** Exact type matching between Direct API and MCP
- [ ] **Value Range Validation:** Confidence scores within expected ranges
- [ ] **Error Taxonomy:** Standardized error codes with actionable hints

### **Gate 3: Enhanced Observability** ✅
- [ ] **Correlation IDs:** All requests tracked with unique identifiers
- [ ] **Error Categories:** Classification system for all error types
- [ ] **Performance Metrics:** Latency, throughput, resource usage per tool
- [ ] **Constitutional Metrics:** Real-time compliance scoring for Articles 1-8
- [ ] **Circuit Breaker Metrics:** State transitions and recovery times tracked
- [ ] **Budget Tracking:** GPU/token usage with alerts and enforcement

### **Gate 4: Transport Security** ✅
- [ ] **Transport Selection:** Automatic selection based on client and environment
- [ ] **TLS Configuration:** Mandatory encryption for all network transports
- [ ] **Certificate Management:** Proper cert/key handling for production
- [ ] **mTLS Support:** Mutual authentication for high-security scenarios
- [ ] **Process Isolation:** Resource limits for STDIO transport
- [ ] **Connection Monitoring:** Active connection tracking and limits

---

## Updated Timeline with Enhancements

### **Week 1: Enhanced Security Foundation (Days 1-7)**
- **Days 1-2:** Secret store integration, JWT rotation system
- **Days 3-4:** Enhanced rate limiting with per-tool limits
- **Days 5-6:** Circuit breaker implementation with state management
- **Day 7:** PII sanitization and audit logging enhancement

### **Week 2: Schema & Testing Enhancement (Days 8-14)**  
- **Days 8-9:** JSON schema definition and validation framework
- **Days 10-11:** Deterministic test fixtures and enhanced comparison tests
- **Days 12-13:** Error taxonomy implementation with standardized responses
- **Day 14:** Enhanced observability with correlation ID tracking

### **Week 3: Transport Security & Integration (Days 15-21)**
- **Days 15-16:** Transport selection logic and TLS configuration
- **Days 17-18:** Claude Code integration with enhanced STDIO transport
- **Days 19-20:** Cursor integration with secure HTTPS transport
- **Day 21:** End-to-end security testing and vulnerability assessment

---

## Monitoring & Alerting Enhancements

### **Real-time Security Dashboards**
```python
class EnhancedSecurityDashboard:
    """GPT-5: Comprehensive security monitoring"""
    
    ALERT_THRESHOLDS = {
        "auth_failure_rate": 0.05,      # 5% auth failure rate
        "rate_limit_hit_rate": 0.10,    # 10% of requests hitting limits
        "circuit_breaker_opens": 3,     # 3 circuit breaker opens per hour
        "pii_detection_rate": 0.01,     # 1% of logs containing PII
        "budget_usage_warning": 0.80,   # 80% of daily budget used
        "budget_usage_critical": 0.95   # 95% of daily budget used
    }
    
    async def monitor_security_metrics(self):
        """Continuous security monitoring with automated alerts"""
        
        while True:
            metrics = await self.collect_security_metrics()
            
            # Check all thresholds
            for metric_name, threshold in self.ALERT_THRESHOLDS.items():
                current_value = metrics.get(metric_name, 0)
                
                if current_value > threshold:
                    await self.trigger_security_alert(metric_name, current_value, threshold)
                    
            await asyncio.sleep(60)  # Check every minute
```

### **Constitutional Compliance Enhanced Monitoring**
```python
class EnhancedComplianceMonitor:
    """Enhanced constitutional compliance monitoring following GPT-5 recommendations"""
    
    async def validate_article_compliance(self) -> Dict[str, float]:
        """Enhanced compliance validation with specific metrics"""
        
        return {
            "article_1_honesty": await self.measure_data_honesty_rate(),
            "article_4_transparency": await self.measure_audit_coverage(),
            "article_6_validation": await self.measure_validation_success_rate(), 
            "article_8_ethics": await self.measure_resource_responsibility(),
            
            # GPT-5: Additional security-focused metrics
            "security_posture": await self.measure_security_score(),
            "error_handling_quality": await self.measure_error_response_quality(),
            "schema_compliance": await self.measure_schema_validation_rate()
        }
```

---

## Production Deployment Configuration

### **Enhanced Environment Configuration**
```bash
# GPT-5 Enhanced Security Configuration
export MCP_SECRET_STORE_TYPE="windows_credential_manager"  # or "system_keyring"
export MCP_JWT_ROTATION_HOURS=6
export MCP_JWT_OVERLAP_MINUTES=30
export MCP_TLS_CERT_PATH="/etc/ssl/certs/hak-gal-mcp.crt"
export MCP_TLS_KEY_PATH="/etc/ssl/private/hak-gal-mcp.key"

# Enhanced Rate Limiting
export MCP_RATE_LIMIT_QUERY_KB_CLAUDE=30
export MCP_RATE_LIMIT_QUERY_KB_CURSOR=20
export MCP_RATE_LIMIT_REASONING_CLAUDE=10
export MCP_RATE_LIMIT_REASONING_CURSOR=8

# Circuit Breaker Configuration
export MCP_CIRCUIT_FAILURE_THRESHOLD=5
export MCP_CIRCUIT_RECOVERY_TIMEOUT=60
export MCP_CIRCUIT_HALF_OPEN_CALLS=3

# Enhanced Monitoring
export MCP_CORRELATION_ID_ENABLED=true
export MCP_PII_SANITIZATION_ENABLED=true
export MCP_AUDIT_LOG_LEVEL=INFO
export MCP_SECURITY_ALERTS_WEBHOOK_URL="https://alerts.company.com/mcp"
```

---

## Success Criteria (Enhanced KPIs)

### **Security KPIs**
- **Authentication Success Rate:** >99.5%
- **Token Rotation Success:** 100% successful rotations
- **Secret Access Audit:** 100% coverage
- **PII Detection Rate:** <0.1% in logs
- **Circuit Breaker Recovery:** <60 seconds average

### **Quality KPIs** 
- **Schema Validation Success:** 100%
- **Error Response Quality:** Standardized format in 100% of cases
- **Correlation ID Coverage:** 100% of requests tracked
- **Deterministic Test Pass Rate:** 100%
- **Type Equivalence:** 100% match between Direct API and MCP

### **Constitutional Compliance KPIs**
- **Article 1 (Honesty):** 100% real data responses
- **Article 4 (Transparency):** 100% audit coverage 
- **Article 6 (Validation):** >99% empirical validation success
- **Article 8 (Ethics):** 100% resource budget compliance

---

## Conclusion

These GPT-5-validated enhancements transform the MVP from a functional prototype into a production-ready, enterprise-grade MCP integration. The enhanced security, observability, and quality controls ensure that the foundation is solid enough to support the advanced capabilities planned for future phases.

**Key Implementation Principles:**
1. **Security First:** Every component designed with security as primary consideration
2. **Observable by Design:** Complete visibility into system operations and compliance
3. **Quality Gates:** No progression without proven stability and compliance
4. **Defense in Depth:** Multiple layers of protection and validation
5. **Constitutional Alignment:** Every enhancement supports HAK/GAL Articles 1-8

The enhanced MVP provides the bulletproof foundation required for revolutionary AI capabilities.

---

**Document Authority:** GPT-5 Validated Technical Specifications  
**Implementation Priority:** CRITICAL - All enhancements mandatory  
**Quality Gate Dependency:** Phase 2 blocked until all enhancements complete  
**Review Cycle:** Weekly validation against GPT-5 criteria

**Document Version:** 1.0 (GPT-5 Enhanced)  
**Last Updated:** 2025-08-13  
**Next Review:** 2025-08-20  
**Implementation Deadline:** 2025-08-27

---

*These enhancements represent the minimum viable security and quality standards for HAK-GAL MCP integration. Implementation of all specified controls is mandatory before proceeding to Phase 2.*
