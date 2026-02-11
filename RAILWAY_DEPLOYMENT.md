# Multi-Agent HR Intelligence Platform - Railway Deployment Guide

Complete guide for deploying Multi-Agent HR Intelligence Platform to Railway.app with PostgreSQL.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Detailed Setup](#detailed-setup)
5. [Environment Variables](#environment-variables)
6. [Database Configuration](#database-configuration)
7. [Deployment Process](#deployment-process)
8. [Post-Deployment](#post-deployment)
9. [Monitoring & Maintenance](#monitoring--maintenance)
10. [Troubleshooting](#troubleshooting)

---

## Overview

Railway is a modern platform-as-a-service (PaaS) that simplifies deployment. This guide walks through deploying Multi-Agent HR Intelligence Platform with:

- **Application:** FastAPI + LangGraph AI agents
- **Database:** PostgreSQL (managed by Railway)
- **Runtime:** Python 3.10 with Gunicorn + Uvicorn workers
- **Deployment:** Automated from GitHub
- **Scaling:** 4 workers, auto-restart on failure

**Architecture:**
```
GitHub → Railway → Docker Build → PostgreSQL + App → Public URL
```

**Deployment Time:** 30-40 minutes (first time)

---

## Prerequisites

### Required

- [x] GitHub account with code repository
- [x] Railway account (sign up at https://railway.app/)
- [x] Groq API key (get from https://console.groq.com/)
- [x] Payment method (required for Railway beyond trial)

### Recommended

- [x] Basic terminal/command line knowledge
- [x] Familiarity with environment variables
- [x] Understanding of REST APIs

---

## Quick Start

For experienced users:

```bash
# 1. Push code to GitHub
git push origin main

# 2. Create Railway project from GitHub
# Go to: https://railway.app/ → New Project → Deploy from GitHub

# 3. Add PostgreSQL service
# Click: New Service → PostgreSQL

# 4. Set environment variables
GROQ_API_KEY=your_groq_api_key
SECRET_KEY=your_generated_secret
ENVIRONMENT=production

# 5. Deploy
# Railway automatically deploys on push to main
```

That's it! See sections below for detailed instructions.

---

## Detailed Setup

### Step 1: Prepare Your Code

Ensure your repository has these files (already included):

```
.
├── railway.json          # Railway configuration
├── Procfile             # Process definitions
├── requirements.txt     # Python dependencies
├── scripts/
│   └── railway_init.py # Initialization script
├── src/                # Application code
└── .railway/           # Railway helpers
    ├── environment-template.txt
    ├── deployment-checklist.md
    └── troubleshooting.md
```

**Verify locally:**
```bash
# Test that app runs locally
python -m src.api.app

# Run tests
pytest

# Check Docker build (optional)
docker build -t smartsupport .
```

---

### Step 2: Create Railway Account

1. Go to https://railway.app/
2. Click "Start a New Project"
3. Sign up with GitHub (recommended)
4. Verify your email
5. Add payment method
   - Hobby plan: $5/month
   - Free trial: Available for testing

---

### Step 3: Create New Project

#### Option A: Deploy from GitHub (Recommended)

1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Authorize Railway to access your GitHub
4. Select repository: `your-username/smartsupport-ai`
5. Select branch: `main`
6. Railway automatically detects Python project

#### Option B: Deploy from Local

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Link to repository
railway link

# Deploy
railway up
```

---

### Step 4: Add PostgreSQL Database

1. In your Railway project, click "New Service"
2. Select "Database"
3. Choose "PostgreSQL"
4. Wait 1-2 minutes for provisioning
5. **Important:** Railway automatically creates `DATABASE_URL` environment variable
6. Verify variable exists:
   - Go to PostgreSQL service
   - Click "Variables"
   - Confirm `DATABASE_URL` is present

**Database Details:**
- **Version:** PostgreSQL 14
- **Storage:** 1GB (Hobby) / 10GB (Pro)
- **Backups:** Automatic daily backups
- **SSL:** Enabled by default

---

### Step 5: Configure Environment Variables

#### Navigate to Variables
- Click on your app service (not database)
- Go to "Variables" tab
- Click "RAW Editor" for easier editing

#### Add Required Variables

```bash
# REQUIRED - Must be set manually
GROQ_API_KEY=gsk_your_groq_api_key_here
SECRET_KEY=your_secret_key_here
ENVIRONMENT=production

# AUTO-PROVIDED - Railway sets these automatically
# DATABASE_URL=postgresql://...  (don't set manually)
# PORT=8000                      (don't set manually)
# RAILWAY_ENVIRONMENT=production (don't set manually)
```

#### Generate SECRET_KEY

**Option 1: Python**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Option 2: OpenSSL**
```bash
openssl rand -base64 32
```

**Option 3: Online Generator**
- Use: https://randomkeygen.com/
- Select: CodeIgniter Encryption Key

#### Get GROQ_API_KEY

1. Go to https://console.groq.com/
2. Sign up / Login
3. Navigate to "API Keys"
4. Click "Create API Key"
5. Copy the key (starts with `gsk_`)
6. Paste into Railway

#### Optional Variables

```bash
# Optional - Customize if needed
LOG_LEVEL=INFO
LLM_MODEL=llama-3.3-70b-versatile
LLM_TEMPERATURE=0.0
LLM_MAX_TOKENS=1000
RATE_LIMIT_PER_MINUTE=60
```

---

## Environment Variables

### Complete Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GROQ_API_KEY` | [DONE] Yes | - | Groq AI API key for LLM operations |
| `SECRET_KEY` | [DONE] Yes | - | Secret key for JWT token signing |
| `DATABASE_URL` | Auto | - | PostgreSQL connection string (Railway auto-sets) |
| `PORT` | Auto | 8000 | Application port (Railway auto-sets) |
| `ENVIRONMENT` | [DONE] Yes | development | Set to `production` for Railway |
| `RAILWAY_ENVIRONMENT` | Auto | - | Railway environment name (auto-set) |
| `LOG_LEVEL` | No | INFO | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `LLM_MODEL` | No | llama-3.3-70b-versatile | Groq model to use |
| `LLM_TEMPERATURE` | No | 0.0 | LLM temperature (0.0-2.0) |
| `LLM_MAX_TOKENS` | No | 1000 | Max tokens per LLM response |
| `OPENAI_API_KEY` | No | - | Optional OpenAI API key as fallback |

### Environment Variables Template

See `.railway/environment-template.txt` for a complete template.

---

## Database Configuration

### Connection Details

Railway automatically provides:
- **DATABASE_URL**: Full PostgreSQL connection string
- **SSL:** Enabled by default
- **Pooling:** Configured in `src/database/connection.py`

### Connection Pool Settings

Current configuration (production):
```python
pool_size=10         # 10 connections
max_overflow=20      # Up to 30 total connections
pool_recycle=3600    # Recycle every hour
pool_pre_ping=True   # Verify before use
sslmode=require      # SSL required
```

### Database Initialization

During deployment, `scripts/railway_init.py` automatically:
1. Checks database connection
2. Creates all tables
3. Verifies schema
4. Runs health checks

### Manual Database Operations

```bash
# Connect to database
railway run psql $DATABASE_URL

# Run migrations
railway run python scripts/railway_init.py

# Backup database
railway run pg_dump $DATABASE_URL > backup.sql

# Restore database
railway run psql $DATABASE_URL < backup.sql

# Check table structure
railway run psql $DATABASE_URL -c "\dt"
```

---

## Deployment Process

### Automatic Deployment

Railway automatically deploys when:
1. Code is pushed to `main` branch
2. Environment variables are changed
3. Manual redeploy is triggered

### Deployment Flow

```
1. Git Push
   ↓
2. Railway Detects Change
   ↓
3. Build Phase
   ├── Install dependencies (pip install -r requirements.txt)
   ├── Build application
   └── Create deployment image
   ↓
4. Release Phase (Procfile: release)
   ├── Run scripts/railway_init.py
   ├── Initialize database
   ├── Verify connections
   └── Health check
   ↓
5. Deploy Phase (Procfile: web)
   ├── Start Gunicorn with 4 workers
   ├── Bind to $PORT
   └── Health check at /api/v1/health
   ↓
6. Live [DONE]
```

### Build Configuration

**railway.json:**
```json
{
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "gunicorn src.api.app:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT",
    "healthcheckPath": "/api/v1/health",
    "healthcheckTimeout": 100
  }
}
```

### Process Configuration

**Procfile:**
```
web: gunicorn src.api.app:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120
release: python scripts/railway_init.py
```

---

## Post-Deployment

### 1. Verify Deployment

#### Check Health Endpoint
```bash
curl https://your-app.up.railway.app/api/v1/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "version": "2.2.0",
  "agent_ready": true
}
```

#### Check API Documentation
Visit: `https://your-app.up.railway.app/docs`

Should show interactive Swagger API documentation.

#### Test a Query
```bash
curl -X POST https://your-app.up.railway.app/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Hello, I need help with billing",
    "user_id": "test_user_123"
  }'
```

---

### 2. Monitor Logs

```bash
# Real-time logs
railway logs --tail

# Filter errors
railway logs | grep ERROR

# Last 100 lines
railway logs --tail 100
```

**What to look for:**
- [DONE] "Database initialized successfully"
- [DONE] "Using PostgreSQL with SSL (production)"
- [DONE] "Health check passed"
- [FAIL] Any errors or warnings

---

### 3. Custom Domain (Optional)

#### Generate Railway Domain
1. Go to Settings → Domains
2. Click "Generate Domain"
3. Get URL like: `smartsupport-ai-production.up.railway.app`

#### Add Custom Domain
1. Click "Custom Domain"
2. Enter: `api.yourdomain.com`
3. Add DNS records as shown:
   ```
   CNAME api.yourdomain.com → <your-app>.up.railway.app
   ```
4. Wait for SSL certificate (automatic, 1-5 minutes)
5. Verify: `https://api.yourdomain.com/api/v1/health`

---

### 4. Enable Metrics

Railway automatically tracks:
- **CPU Usage:** % utilization
- **Memory Usage:** MB used / available
- **Network:** Inbound/outbound traffic
- **Response Times:** P50, P95, P99
- **Request Count:** Requests per minute

**Access Metrics:**
- Dashboard → Your Service → Metrics tab

---

## Monitoring & Maintenance

### Daily Checks

- [ ] Check application status (green/red indicator)
- [ ] Review error logs: `railway logs | grep ERROR`
- [ ] Monitor response times (should be <2s)
- [ ] Verify database connection pool health

### Weekly Tasks

- [ ] Review resource usage trends
- [ ] Check for dependency updates
- [ ] Review security advisories
- [ ] Backup database (Railway auto-backups, but verify)
- [ ] Test key user flows

### Monthly Tasks

- [ ] Review and optimize slow queries
- [ ] Update dependencies: `pip list --outdated`
- [ ] Review Railway billing
- [ ] Test disaster recovery procedure
- [ ] Rotate SECRET_KEY (if needed)

---

### Uptime Monitoring

**Recommended Services:**
- UptimeRobot (free tier available)
- Pingdom
- StatusCake

**Configuration:**
- **URL to monitor:** `https://your-app.up.railway.app/api/v1/health`
- **Interval:** Every 5 minutes
- **Alert:** Email/SMS on downtime

---

### Logging

**View Logs:**
```bash
# Real-time
railway logs --tail

# Specific service
railway logs --service <service-name>

# Export logs
railway logs > logs.txt
```

**Log Levels:**
- `DEBUG`: Detailed info for debugging
- `INFO`: General information (default)
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical errors

**Change Log Level:**
```bash
# In Railway variables
LOG_LEVEL=DEBUG  # For troubleshooting
LOG_LEVEL=INFO   # For production
```

---

## Troubleshooting

### Quick Diagnostics

```bash
# 1. Check service status
railway status

# 2. View recent logs
railway logs --tail 100

# 3. Check environment variables
railway vars

# 4. Restart service
railway restart

# 5. Redeploy
railway up
```

---

### Common Issues

#### Deployment Fails

**Symptoms:** Build or deployment fails

**Solutions:**
1. Check logs: `railway logs`
2. Verify all required env vars are set
3. Test build locally: `pip install -r requirements.txt`
4. Check Python version compatibility

See `.railway/troubleshooting.md` for detailed solutions.

---

#### Database Connection Errors

**Symptoms:** `OperationalError: could not connect to server`

**Solutions:**
1. Verify PostgreSQL service is running
2. Check `DATABASE_URL` is set
3. Enable SSL: Already configured in code
4. Check firewall/network settings

---

#### Health Check Fails

**Symptoms:** `Health check timeout`

**Solutions:**
1. Increase timeout in `railway.json`
2. Check `/api/v1/health` endpoint exists
3. Verify app binds to `$PORT`
4. Review startup logs

---

### Get Help

1. **Project Documentation:**
   - `.railway/deployment-checklist.md`
   - `.railway/troubleshooting.md`
   - `DOCKER_README.md`
   - `CI_CD_SETUP.md`

2. **Railway Resources:**
   - Docs: https://docs.railway.app/
   - Discord: https://discord.gg/railway
   - Status: https://status.railway.app/

3. **Project Support:**
   - GitHub Issues
   - Check logs: `railway logs`
   - Review recent commits

---

## Scaling & Performance

### Horizontal Scaling

**Increase workers:**
```json
// In Procfile or railway.json
--workers 6  // From 4
```

**Considerations:**
- More workers = more memory usage
- Monitor CPU/memory metrics
- Hobby plan: 512MB RAM limit
- Pro plan: Up to 8GB RAM

---

### Vertical Scaling

**Upgrade Railway Plan:**
- **Hobby:** $5/month, 512MB RAM, 1GB storage
- **Pro:** $20/month, 8GB RAM, 10GB storage

**When to upgrade:**
- Memory usage consistently >80%
- CPU usage consistently >70%
- Need more database storage
- Require faster builds

---

### Performance Optimization

1. **Database:**
   - Add indexes on frequently queried columns
   - Use connection pooling (already configured)
   - Enable query caching

2. **Application:**
   - Use async operations where possible
   - Implement caching (Redis)
   - Optimize LLM token usage

3. **Infrastructure:**
   - Use CDN for static assets
   - Enable Railway's edge caching
   - Consider adding Redis for session storage

---

## Security Best Practices

### Secrets Management

- [DONE] All secrets in Railway environment variables
- [DONE] No hardcoded credentials in code
- [FAIL] Never commit `.env` to repository
- [DONE] Rotate `SECRET_KEY` every 90 days
- [DONE] Rotate `GROQ_API_KEY` if compromised

### Database Security

- [DONE] SSL enabled for all connections
- [DONE] Connection pooling prevents exhaustion
- [DONE] Railway handles firewall rules
- [DONE] Automatic daily backups
- [DONE] Private network (not publicly accessible)

### Application Security

- [DONE] HTTPS enforced (Railway automatic)
- [DONE] CORS configured appropriately
- [DONE] Rate limiting enabled
- [DONE] Input validation on all endpoints
- [DONE] SQL injection protection (SQLAlchemy ORM)

---

## Cost Estimation

### Railway Pricing

**Hobby Plan:** $5/month
- 512MB RAM
- 1GB disk
- Unlimited outbound bandwidth

**Pro Plan:** $20/month
- 8GB RAM
- 10GB disk
- Unlimited outbound bandwidth
- Priority support

### Additional Costs

- **PostgreSQL:** Included in plan
- **Groq API:** Pay-per-use (check Groq pricing)
- **Domain:** $10-15/year (optional)
- **Monitoring:** Free tier available (UptimeRobot)

**Estimated Monthly Cost:**
- Development/Testing: $5-10
- Production (low traffic): $20-30
- Production (high traffic): $50-100+

---

## Backup & Recovery

### Automatic Backups

Railway provides:
- **Frequency:** Daily automatic backups
- **Retention:** 7 days (Hobby), 14 days (Pro)
- **Location:** Railway's secure storage

### Manual Backup

```bash
# Backup database
railway run pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Backup environment variables
railway vars > env_backup.txt

# Backup code
git push origin main
```

### Restore Procedure

```bash
# Restore from backup
railway run psql $DATABASE_URL < backup_20241124.sql

# Verify restore
railway run psql $DATABASE_URL -c "SELECT COUNT(*) FROM conversations;"
```

---

## CI/CD Integration

Railway integrates with GitHub Actions for full CI/CD.

See `CI_CD_SETUP.md` for complete GitHub Actions integration.

**Workflow:**
1. Push to `main` → GitHub Actions run tests
2. Tests pass → Railway auto-deploys
3. Deployment success → Health check
4. Notify team (optional)

---

## Checklist Summary

Use `.railway/deployment-checklist.md` for complete checklist.

**Quick Checklist:**
- [ ] Code pushed to GitHub
- [ ] Railway project created
- [ ] PostgreSQL service added
- [ ] Environment variables set (GROQ_API_KEY, SECRET_KEY)
- [ ] Deployment successful
- [ ] Health check passing
- [ ] API documentation accessible
- [ ] Test query works
- [ ] Logs reviewed
- [ ] Monitoring enabled

---

## Next Steps

After successful deployment:

1. **Test thoroughly:**
   - All API endpoints
   - Different query types
   - Error handling
   - Performance under load

2. **Set up monitoring:**
   - Uptime monitoring
   - Error tracking
   - Performance metrics
   - Log aggregation

3. **Document:**
   - API endpoints for team
   - Environment variables
   - Deployment procedure
   - Rollback procedure

4. **Optimize:**
   - Review slow queries
   - Add caching if needed
   - Optimize LLM prompts
   - Fine-tune worker count

---

## Resources

- **Railway:** https://railway.app/
- **Railway Docs:** https://docs.railway.app/
- **Railway CLI:** https://docs.railway.app/develop/cli
- **Project README:** `README.md`
- **Docker Guide:** `DOCKER_README.md`
- **CI/CD Guide:** `CI_CD_SETUP.md`
- **Troubleshooting:** `.railway/troubleshooting.md`

---

**Last Updated:** 2024-11-24
**Version:** 1.0.0
**Status:** [DONE] Production Ready

Need help? Check `.railway/troubleshooting.md` or create an issue in the repository.
