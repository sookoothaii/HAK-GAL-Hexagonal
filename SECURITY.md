# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| < 2.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability within HAK-GAL Hexagonal, please follow these steps:

1. **Do NOT** open a public issue
2. Send an email to: [Create security contact]
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if available)

## Security Measures

### Authentication
- API Key authentication for all endpoints
- Write token required for modifications
- Audit logging for all write operations

### Code Execution
- Sandboxed environment with timeout limits
- No access to system resources
- Limited memory allocation
- No network access from sandbox

### Data Protection
- SQLite with WAL mode for data integrity
- Regular automated backups
- No sensitive data in logs

### Dependencies
- Regular dependency updates
- Security scanning via GitHub Dependabot
- Only trusted packages used

## Best Practices

### For Users
- Keep API keys secure
- Use environment variables for sensitive data
- Regularly rotate credentials
- Monitor audit logs

### For Contributors
- Never commit sensitive data
- Use `.env` files (not tracked)
- Follow secure coding practices
- Test security implications

## Response Time

We aim to:
- Acknowledge receipt within 48 hours
- Provide initial assessment within 1 week
- Release patches for critical issues ASAP

## Disclosure Policy

- We follow responsible disclosure
- Security advisories will be published after patches
- Credit given to reporters (unless anonymity requested)

Thank you for helping keep HAK-GAL Hexagonal secure!
