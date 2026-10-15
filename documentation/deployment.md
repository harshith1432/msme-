# Production Deployment Guide

## 1. Prerequisites

- Linux VPS / Cloud VM (Ubuntu 22.04 LTS or Debian 12 recommended)
- Docker 24+ and Docker Compose v2+
- Domain name with DNS A records pointed to server IP
- TLS certificate (Let's Encrypt / Certbot)

## 2. Quick Deployment (Docker Compose)

1. Clone repository to server:
   ```bash
   git clone <repo-url> /opt/msme-navigator
   cd /opt/msme-navigator
   ```

2. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your PostgreSQL credentials, Redis URL, S3 keys, and SECRET_KEY
   nano .env
   ```

3. Launch production stack:
   ```bash
   docker compose -f compose.production.yaml up -d --build
   ```

4. Verify health:
   ```bash
   ./scripts/health_check.sh http://127.0.0.1
   ```

## 3. Database Migrations & Seeding

Migrations and regulatory seeding execute automatically at initial container boot. To manually run database migrations:
```bash
docker compose -f compose.production.yaml exec web flask db upgrade
```
