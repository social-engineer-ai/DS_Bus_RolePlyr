# Pre-Deployment Checklist

> **IMPORTANT:** Complete ALL items in this checklist before deploying to production.

## Critical Security Items

### Authentication (Currently Mock)

- [ ] **Replace mock authentication with real OAuth 2.0**
  - Implement Google OAuth
  - Implement university SSO (if required)
  - Remove all mock auth endpoints (`/mock-login`, `/mock-users`)
  - Remove `MOCK_USERS` dictionary from codebase

- [ ] **Set up proper session management**
  - Use secure, HTTP-only cookies
  - Implement proper token refresh
  - Add session expiration handling

- [ ] **Implement HTTPS/TLS**
  - Obtain SSL certificate
  - Configure reverse proxy (nginx/caddy)
  - Enforce HTTPS redirects

### Database & Secrets

- [ ] **Configure production database**
  - Use strong, unique password
  - Enable SSL connections
  - Set up connection pooling
  - Configure backups

- [ ] **Secure all secrets**
  - Use secrets manager (AWS Secrets Manager, HashiCorp Vault)
  - Rotate all development secrets
  - Never commit `.env` files

- [ ] **Update secret key**
  - Generate new `SECRET_KEY` for production
  - Use cryptographically secure random string

### API Security

- [ ] **Set up rate limiting**
  - Limit login attempts
  - Limit API calls per user
  - Add DDoS protection

- [ ] **Configure CORS properly**
  - Remove wildcard origins
  - Whitelist only production domains

- [ ] **Add request validation**
  - Validate all inputs
  - Sanitize user content
  - Limit request sizes

### Compliance

- [ ] **FERPA compliance review**
  - Verify student data handling
  - Check data retention policies
  - Review access controls

- [ ] **Privacy policy**
  - Create/update privacy policy
  - Add cookie consent
  - Document data usage

### Infrastructure

- [ ] **Set up logging and monitoring**
  - Application logs
  - Error tracking (Sentry)
  - Performance monitoring
  - Alerting

- [ ] **Configure backups**
  - Database backups
  - Disaster recovery plan

- [ ] **Security audit**
  - Dependency vulnerability scan
  - Code review
  - Penetration testing (if required)

## Pre-Launch Verification

- [ ] Run full test suite
- [ ] Load testing completed
- [ ] Security scan completed
- [ ] Documentation updated
- [ ] Team trained on production procedures

---

## Quick Reference: Files to Modify

| File | Action |
|------|--------|
| `backend/app/routers/auth.py` | Replace mock auth with OAuth |
| `backend/app/config.py` | Update production settings |
| `docker-compose.yml` | Use production config |
| `.env` | Use production secrets |
| `frontend/src/app/page.tsx` | Remove dev warning |

---

*Last Updated: [Date]*
*Reviewed By: [Name]*
