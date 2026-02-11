# Railway Deployment Checklist

Complete this checklist step-by-step to successfully deploy Multi-Agent HR Intelligence Platform to Railway.

## Pre-Deployment (Local Setup)

### 1. Code Preparation
- [ ] All code committed to GitHub
- [ ] Tests passing locally (`pytest`)
- [ ] Linting passing (`flake8 src/`)
- [ ] Formatting correct (`black --check src/`)
- [ ] Docker build successful (optional)
- [ ] `.env` file NOT committed (check `.gitignore`)

### 2. GitHub Setup
- [ ] Code pushed to GitHub repository
- [ ] Repository is public or accessible to Railway
- [ ] GitHub Actions workflows passing
- [ ] Latest commit is on `main` branch

---

## Railway Account Setup

### 3. Create Railway Account
- [ ] Sign up at https://railway.app/
- [ ] Verify email address
- [ ] Add payment method (required for production)
- [ ] Select appropriate plan (Hobby/Pro)

### 4. Create New Project
- [ ] Click "New Project" in Railway dashboard
- [ ] Select "Deploy from GitHub repo"
- [ ] Connect GitHub account to Railway
- [ ] Select your repository
- [ ] Choose `main` branch for deployment

---

## Service Configuration

### 5. Add PostgreSQL Database
- [ ] Click "New Service" in Railway
- [ ] Select "PostgreSQL" from database options
- [ ] Wait for database provisioning (1-2 minutes)
- [ ] Verify `DATABASE_URL` variable appears automatically
- [ ] Note: Database URL is auto-injected into your app

### 6. Configure Environment Variables
Navigate to: Project → Variables → RAW Editor

**Required Variables (add these manually):**
- [ ] `GROQ_API_KEY` - Your Groq API key
  - Get from: https://console.groq.com/
  - Example: `gsk_...`

- [ ] `SECRET_KEY` - JWT secret key
  - Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
  - Example: `s7K9mP2nQ5tR8vW1xY4zA6bC3dE0fG7h`

- [ ] `ENVIRONMENT` - Set to `production`

**Auto-Provided by Railway (verify these exist):**
- [ ] `DATABASE_URL` - PostgreSQL connection string
- [ ] `PORT` - Application port number
- [ ] `RAILWAY_ENVIRONMENT` - Railway environment name

**Optional Variables:**
- [ ] `OPENAI_API_KEY` - If using OpenAI as fallback
- [ ] `LOG_LEVEL` - Set to `INFO` or `DEBUG`
- [ ] `LLM_MODEL` - Default is `llama-3.3-70b-versatile`

---

## Deployment

### 7. Trigger Deployment
- [ ] Click "Deploy" in Railway dashboard
- [ ] Wait for build process to start
- [ ] Monitor build logs in real-time

**Build Steps to Monitor:**
1. [ ] Installing dependencies (pip install)
2. [ ] Building application
3. [ ] Running `railway_init.py` script
4. [ ] Database initialization
5. [ ] Health check passing

### 8. Verify Deployment
- [ ] Build completes successfully (green checkmark)
- [ ] No errors in deployment logs
- [ ] Service shows "Active" status
- [ ] Public URL is generated

---

## Post-Deployment Verification

### 9. Test Application
- [ ] Click on public URL (e.g., `https://smartsupport-ai.up.railway.app`)
- [ ] Health check endpoint works: `/api/v1/health`
  - Expected response: `{"status": "healthy", "version": "2.2.0", "agent_ready": true}`
- [ ] API documentation accessible: `/docs`
- [ ] Test a sample query via API

### 10. Database Verification
- [ ] Check logs for successful database connection
- [ ] Verify tables were created
- [ ] Test database queries through API

### 11. Monitor Logs
- [ ] Open Railway logs tab
- [ ] Check for any errors or warnings
- [ ] Verify application is handling requests
- [ ] Check database connection logs

---

## Optional Configuration

### 12. Custom Domain (Optional)
- [ ] Go to Settings → Domains
- [ ] Click "Generate Domain" or "Custom Domain"
- [ ] Add custom domain (e.g., `api.yourdomain.com`)
- [ ] Configure DNS records as shown
- [ ] Wait for SSL certificate generation (automatic)
- [ ] Verify custom domain works

### 13. Environment Separation (Optional)
- [ ] Create separate Railway projects for staging/prod
- [ ] Configure different GitHub branches
- [ ] Set up staging environment variables
- [ ] Test staging before promoting to production

---

## CI/CD Integration

### 14. GitHub Actions Integration
- [ ] Verify GitHub Actions deploy workflow exists
- [ ] Add Railway secrets to GitHub:
  - `RAILWAY_TOKEN` - Railway API token
  - `RAILWAY_PROJECT_ID` - Project ID from Railway
  - `RAILWAY_APP_URL` - Your Railway app URL
- [ ] Test automatic deployment on push to main
- [ ] Verify CI/CD pipeline runs successfully

---

## Monitoring & Maintenance

### 15. Set Up Monitoring
- [ ] Enable Railway metrics dashboard
- [ ] Monitor CPU and memory usage
- [ ] Set up uptime monitoring (e.g., UptimeRobot)
- [ ] Configure log aggregation if needed
- [ ] Set up error tracking (optional: Sentry)

### 16. Backup Strategy
- [ ] Enable automatic PostgreSQL backups in Railway
- [ ] Document backup retention policy
- [ ] Test database restore procedure
- [ ] Export environment variables backup

---

## Security Checklist

### 17. Security Review
- [ ] All secrets stored in Railway environment variables
- [ ] No hardcoded credentials in code
- [ ] HTTPS enabled (automatic on Railway)
- [ ] Database connections use SSL
- [ ] API rate limiting configured
- [ ] CORS configured if needed
- [ ] Secret rotation schedule documented

---

## Documentation

### 18. Update Documentation
- [ ] Update README with Railway deployment URL
- [ ] Document all environment variables used
- [ ] Create runbook for common operations
- [ ] Document rollback procedure
- [ ] Share access with team members (if applicable)

---

## Troubleshooting Commands

If deployment fails, try these:

```bash
# View logs
railway logs

# Check service status
railway status

# Restart service
railway restart

# SSH into running container
railway run bash

# Run database migrations manually
railway run python scripts/railway_init.py

# Check environment variables
railway vars
```

---

## Success Criteria

Your deployment is successful when:

- [x] Application is accessible via public URL
- [x] Health check endpoint returns `{"status": "healthy"}`
- [x] API documentation is visible at `/docs`
- [x] Database queries work correctly
- [x] No errors in Railway logs
- [x] Sample AI queries return responses
- [x] All environment variables are set correctly

---

## Estimated Time

- Initial setup: 15-20 minutes
- First deployment: 5-10 minutes
- Verification: 5-10 minutes
- **Total: 30-40 minutes**

---

## Need Help?

- Railway Documentation: https://docs.railway.app/
- Railway Discord: https://discord.gg/railway
- Project Issues: Create issue in GitHub repository
- Check `.railway/troubleshooting.md` for common issues

---

**Last Updated:** 2024-11-24
**Version:** 1.0.0
