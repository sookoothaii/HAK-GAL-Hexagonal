---
title: "Security Enhancement Research Roadmap"
created: "2025-09-21T10:30:00.000000Z"
author: "Claude-Sonnet-4"
topics: ["security", "oauth2", "jwt", "rbac", "mtls", "vault"]
tags: ["security-roadmap", "authentication", "authorization", "enterprise-security", "compliance"]
privacy: "internal"
summary_200: "Umfassende Security-Modernisierung von Basic API-Key zu Enterprise-Grade OAuth2/JWT, RBAC, mTLS und Vault-Integration für HAK-GAL Architektur."
---

# Security Enhancement Research Roadmap

**Version:** 1.0  
**Datum:** 2025-09-21  
**Autor:** Claude-Sonnet-4  
**Status:** Security Research Roadmap  
**Priorität:** HOCH (3-6 Monate)

## 🎯 Security-Modernisierung Übersicht

### Aktuelle Security-Situation
- **Security Score:** 4/10 (Basic, nicht enterprise-grade)
- **Authentication:** API-Key (`hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d`)
- **Authorization:** Keine RBAC, Alles-oder-Nichts Zugriff
- **Transport Security:** HTTP (kein mTLS)
- **Secrets Management:** Hardcoded API-Keys

### Ziel-Security-Architektur
```
┌─────────────────────────────────────────────────────────────────┐
│                    SECURITY STACK 2024                         │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │   OAuth2    │  │     JWT     │  │    RBAC     │  │  Vault  │ │
│  │ (Provider)  │  │  (Tokens)   │  │ (Permissions)│  │(Secrets)│ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │    mTLS     │  │   Audit     │  │   WAF       │  │  SIEM   │ │
│  │(Encryption) │  │ (Logging)   │  │(Protection) │  │(Analysis)│ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 🔐 Phase 1: OAuth2/JWT Authentication (Monate 1-2)

### 1.1 OAuth2 Provider Setup

#### Keycloak Integration
```yaml
# docker-compose.yml
  keycloak:
    image: quay.io/keycloak/keycloak:latest
    ports:
      - "8080:8080"
    environment:
      - KEYCLOAK_ADMIN=admin
      - KEYCLOAK_ADMIN_PASSWORD=admin
      - KC_DB=postgres
      - KC_DB_URL=jdbc:postgresql://postgres:5432/keycloak
      - KC_DB_USERNAME=keycloak
      - KC_DB_PASSWORD=keycloak
    command: start-dev
```

#### Keycloak Configuration
```json
{
  "realm": "hak-gal",
  "clients": [
    {
      "clientId": "hak-gal-frontend",
      "enabled": true,
      "publicClient": true,
      "redirectUris": ["http://localhost:8088/*"],
      "webOrigins": ["http://localhost:8088"]
    },
    {
      "clientId": "hak-gal-backend",
      "enabled": true,
      "serviceAccountsEnabled": true,
      "authorizationServicesEnabled": true
    }
  ],
  "users": [
    {
      "username": "admin",
      "enabled": true,
      "credentials": [
        {
          "type": "password",
          "value": "admin123"
        }
      ]
    }
  ]
}
```

### 1.2 JWT Token Management

#### Flask JWT Implementation
```python
# auth.py
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from functools import wraps
import requests

app.config['JWT_SECRET_KEY'] = 'your-secret-key'
jwt = JWTManager(app)

class AuthService:
    def __init__(self):
        self.keycloak_url = "http://keycloak:8080"
        self.realm = "hak-gal"
    
    def validate_token(self, token):
        """Validate JWT token with Keycloak"""
        url = f"{self.keycloak_url}/realms/{self.realm}/protocol/openid-connect/userinfo"
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(url, headers=headers)
        return response.status_code == 200
    
    def get_user_info(self, token):
        """Get user information from token"""
        url = f"{self.keycloak_url}/realms/{self.realm}/protocol/openid-connect/userinfo"
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(url, headers=headers)
        return response.json() if response.status_code == 200 else None

# Decorator for JWT authentication
def jwt_required_with_validation(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid token'}), 401
        
        token = token.split(' ')[1]
        auth_service = AuthService()
        
        if not auth_service.validate_token(token):
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    return decorated_function
```

### 1.3 Frontend JWT Integration

#### React Authentication Hook
```typescript
// src/hooks/useAuth.ts
import { useState, useEffect } from 'react';
import Keycloak from 'keycloak-js';

const keycloak = new Keycloak({
  url: 'http://localhost:8080',
  realm: 'hak-gal',
  clientId: 'hak-gal-frontend'
});

export const useAuth = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);

  useEffect(() => {
    keycloak.init({ onLoad: 'login-required' })
      .then((authenticated) => {
        setIsAuthenticated(authenticated);
        if (authenticated) {
          setUser(keycloak.tokenParsed);
          setToken(keycloak.token);
        }
      });
  }, []);

  const login = () => keycloak.login();
  const logout = () => keycloak.logout();
  const refreshToken = () => keycloak.updateToken(30);

  return {
    isAuthenticated,
    user,
    token,
    login,
    logout,
    refreshToken
  };
};
```

## 🛡️ Phase 2: Role-Based Access Control (Monate 2-3)

### 2.1 RBAC Permission System

#### Permission Model
```python
# models.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship

# Association tables
user_roles = Table('user_roles',
    Column('user_id', String, ForeignKey('users.id')),
    Column('role_id', String, ForeignKey('roles.id'))
)

role_permissions = Table('role_permissions',
    Column('role_id', String, ForeignKey('roles.id')),
    Column('permission_id', String, ForeignKey('permissions.id'))
)

class User:
    id = Column(String, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String)
    active = Column(Boolean, default=True)
    roles = relationship("Role", secondary=user_roles, back_populates="users")

class Role:
    id = Column(String, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String)
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")

class Permission:
    id = Column(String, primary_key=True)
    resource = Column(String)  # e.g., 'facts', 'users', 'system'
    action = Column(String)    # e.g., 'read', 'write', 'delete', 'admin'
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")
```

#### RBAC Service
```python
# rbac_service.py
class RBACService:
    def __init__(self, db):
        self.db = db
    
    def check_permission(self, user_id, resource, action):
        """Check if user has permission for resource/action"""
        user = User.query.get(user_id)
        if not user or not user.active:
            return False
        
        for role in user.roles:
            for permission in role.permissions:
                if permission.resource == resource and permission.action == action:
                    return True
        return False
    
    def get_user_permissions(self, user_id):
        """Get all permissions for a user"""
        user = User.query.get(user_id)
        if not user:
            return []
        
        permissions = set()
        for role in user.roles:
            for permission in role.permissions:
                permissions.add(f"{permission.resource}:{permission.action}")
        
        return list(permissions)

# RBAC Decorator
def require_permission(resource, action):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = get_jwt_identity()
            rbac_service = RBACService(db)
            
            if not rbac_service.check_permission(user_id, resource, action):
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Usage in API endpoints
@app.route('/api/facts', methods=['GET'])
@jwt_required_with_validation
@require_permission('facts', 'read')
def get_facts():
    # Implementation
    pass

@app.route('/api/facts', methods=['POST'])
@jwt_required_with_validation
@require_permission('facts', 'write')
def create_fact():
    # Implementation
    pass
```

### 2.2 Default Roles and Permissions

#### Initial Data Setup
```python
# seed_data.py
def create_default_roles_and_permissions():
    # Create permissions
    permissions = [
        Permission(id='facts:read', resource='facts', action='read'),
        Permission(id='facts:write', resource='facts', action='write'),
        Permission(id='facts:delete', resource='facts', action='delete'),
        Permission(id='users:read', resource='users', action='read'),
        Permission(id='users:write', resource='users', action='write'),
        Permission(id='system:admin', resource='system', action='admin'),
    ]
    
    # Create roles
    roles = [
        Role(
            id='admin',
            name='Administrator',
            description='Full system access',
            permissions=permissions
        ),
        Role(
            id='researcher',
            name='Researcher',
            description='Read/write access to facts',
            permissions=[p for p in permissions if p.resource == 'facts']
        ),
        Role(
            id='viewer',
            name='Viewer',
            description='Read-only access',
            permissions=[p for p in permissions if p.action == 'read']
        )
    ]
    
    db.session.add_all(permissions + roles)
    db.session.commit()
```

## 🔒 Phase 3: mTLS Implementation (Monate 3-4)

### 3.1 Certificate Management

#### Certificate Authority Setup
```bash
# Create CA
openssl genrsa -out ca-key.pem 4096
openssl req -new -x509 -days 365 -key ca-key.pem -out ca.pem

# Create server certificate
openssl genrsa -out server-key.pem 4096
openssl req -new -key server-key.pem -out server.csr
openssl x509 -req -days 365 -in server.csr -CA ca.pem -CAkey ca-key.pem -out server.pem

# Create client certificate
openssl genrsa -out client-key.pem 4096
openssl req -new -key client-key.pem -out client.csr
openssl x509 -req -days 365 -in client.csr -CA ca.pem -CAkey ca-key.pem -out client.pem
```

### 3.2 Flask mTLS Configuration

#### Flask mTLS Setup
```python
# mtls_config.py
from flask import Flask
import ssl

def create_app():
    app = Flask(__name__)
    
    # mTLS Configuration
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain('server.pem', 'server-key.pem')
    context.load_verify_locations('ca.pem')
    context.verify_mode = ssl.CERT_REQUIRED
    
    return app

# Run with mTLS
if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5002, ssl_context=context)
```

### 3.3 Caddy mTLS Configuration

#### Caddyfile mTLS
```caddyfile
{
    admin off
    metrics
}

:8088 {
    tls server.pem server-key.pem {
        client_auth ca.pem
    }
    
    # ... existing configuration ...
}
```

## 🗄️ Phase 4: Vault Secrets Management (Monate 4-5)

### 4.1 Vault Setup

#### Docker Compose Addition
```yaml
  vault:
    image: vault:latest
    ports:
      - "8200:8200"
    environment:
      - VAULT_DEV_ROOT_TOKEN_ID=myroot
      - VAULT_DEV_LISTEN_ADDRESS=0.0.0.0:8200
    cap_add:
      - IPC_LOCK
    volumes:
      - vault_data:/vault/data
```

### 4.2 Vault Integration

#### Flask Vault Client
```python
# vault_client.py
import hvac
import os

class VaultClient:
    def __init__(self):
        self.client = hvac.Client(url='http://vault:8200')
        self.client.token = os.getenv('VAULT_TOKEN', 'myroot')
    
    def get_secret(self, path, key):
        """Get secret from Vault"""
        try:
            response = self.client.secrets.kv.v2.read_secret_version(path=path)
            return response['data']['data'][key]
        except Exception as e:
            print(f"Error getting secret: {e}")
            return None
    
    def set_secret(self, path, data):
        """Set secret in Vault"""
        try:
            self.client.secrets.kv.v2.create_or_update_secret(
                path=path,
                secret=data
            )
            return True
        except Exception as e:
            print(f"Error setting secret: {e}")
            return False

# Usage in Flask app
vault_client = VaultClient()

@app.route('/api/config')
@jwt_required_with_validation
@require_permission('system', 'admin')
def get_config():
    api_key = vault_client.get_secret('hak-gal/api', 'key')
    db_password = vault_client.get_secret('hak-gal/database', 'password')
    
    return jsonify({
        'api_key_configured': bool(api_key),
        'db_configured': bool(db_password)
    })
```

### 4.3 API Key Migration

#### Migration Script
```python
# migrate_api_keys.py
def migrate_to_vault():
    """Migrate hardcoded API keys to Vault"""
    
    # Store current API key in Vault
    vault_client.set_secret('hak-gal/api', {
        'key': 'hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d',
        'created': '2025-09-21',
        'type': 'legacy'
    })
    
    # Generate new API key
    new_api_key = generate_secure_api_key()
    vault_client.set_secret('hak-gal/api/new', {
        'key': new_api_key,
        'created': datetime.utcnow().isoformat(),
        'type': 'oauth2_jwt'
    })
    
    print("API key migration completed")

def generate_secure_api_key():
    """Generate cryptographically secure API key"""
    import secrets
    return secrets.token_urlsafe(32)
```

## 📊 Phase 5: Audit Logging & Compliance (Monate 5-6)

### 5.1 Audit Logging System

#### Audit Service
```python
# audit_service.py
import json
from datetime import datetime
from flask import request, g

class AuditService:
    def __init__(self, db):
        self.db = db
    
    def log_action(self, user_id, action, resource, details=None):
        """Log user action for audit trail"""
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            timestamp=datetime.utcnow(),
            details=json.dumps(details) if details else None
        )
        
        self.db.session.add(audit_log)
        self.db.session.commit()
    
    def get_audit_trail(self, user_id=None, resource=None, start_date=None, end_date=None):
        """Get audit trail with filters"""
        query = AuditLog.query
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        if resource:
            query = query.filter_by(resource=resource)
        if start_date:
            query = query.filter(AuditLog.timestamp >= start_date)
        if end_date:
            query = query.filter(AuditLog.timestamp <= end_date)
        
        return query.order_by(AuditLog.timestamp.desc()).all()

# Audit decorator
def audit_action(action, resource):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = get_jwt_identity()
            result = f(*args, **kwargs)
            
            # Log the action
            audit_service = AuditService(db)
            audit_service.log_action(
                user_id=user_id,
                action=action,
                resource=resource,
                details={'status_code': result[1] if isinstance(result, tuple) else 200}
            )
            
            return result
        return decorated_function
    return decorator
```

## 🎯 Erfolgsmetriken

### Quantitative Ziele
- **Authentication Success Rate:** 99.9%
- **Authorization Response Time:** <50ms
- **Security Audit Compliance:** 100%
- **Zero Security Vulnerabilities**

### Qualitative Ziele
- Enterprise-Grade Security Standards
- ISO 27001 Compliance Ready
- Zero-Trust Architecture
- Comprehensive Audit Trail

## 🔗 Knowledge Base Integration

### Forschungs-Facts
- `SecurityEnhancementResearch` - Hauptforschungsrichtung
- `ArchitectureResearchDirection2024` - Gesamtkontext

### Nächste Schritte
1. **OAuth2/JWT Setup** (Monate 1-2)
2. **RBAC Implementation** (Monate 2-3)
3. **mTLS Configuration** (Monate 3-4)
4. **Vault Integration** (Monate 4-5)
5. **Audit Logging** (Monate 5-6)

---

**Dokumentation erstellt:** 2025-09-21  
**Implementierungszeitraum:** 6 Monate  
**Status:** Hohe Priorität  
**Ziel:** Security Score 4/10 → 8/10