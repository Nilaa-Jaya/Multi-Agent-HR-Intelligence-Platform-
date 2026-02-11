# GitHub Actions Workflows

This directory contains the CI/CD workflows for Multi-Agent HR Intelligence Platform. Each workflow is designed to automate different aspects of the development and deployment process.

## Workflows Overview

### 1. Test Workflow (`test.yml`)

**Purpose:** Automated testing on every pull request and push

**Triggers:**
- Pull requests to `main` branch
- Pushes to `main` and `develop` branches

**What it does:**
1. Sets up Python 3.10 environment
2. Installs project dependencies (with pip caching for speed)
3. Runs flake8 linting to catch syntax errors
4. Checks code formatting with black
5. Runs pytest with coverage reporting
6. Uploads coverage reports to Codecov
7. Generates test summary

**Requirements:**
- `GROQ_API_KEY` secret (for tests that need API access)

**How to use:**
- Automatically runs on PR creation
- PRs will show test status
- Coverage threshold set to 70%

---

### 2. Docker Build Workflow (`docker-build.yml`)

**Purpose:** Build and push Docker images to GitHub Container Registry

**Triggers:**
- Pushes to `main` branch
- Release creation
- Manual dispatch (via GitHub UI)

**What it does:**
1. Checks out the code
2. Sets up Docker Buildx for multi-platform builds
3. Logs into GitHub Container Registry (ghcr.io)
4. Extracts metadata (tags, labels)
5. Builds Docker image with caching
6. Pushes image to `ghcr.io/YOUR_USERNAME/smartsupport-ai`
7. Tags images with:
   - `latest` (for main branch)
   - Version numbers (for releases)
   - Commit SHA
   - Branch name
8. Runs basic health check
9. Scans for vulnerabilities with Trivy

**Requirements:**
- `GITHUB_TOKEN` (automatically provided)
- Repository must have packages write permission

**Image Tags:**
- `latest` - Latest main branch build
- `main-abc1234` - Specific commit on main
- `v1.0.0` - Release versions
- `staging` - Staging branch builds

**How to use:**
```bash
# Pull latest image
docker pull ghcr.io/YOUR_USERNAME/smartsupport-ai:latest

# Pull specific version
docker pull ghcr.io/YOUR_USERNAME/smartsupport-ai:v1.0.0

# Manual trigger
# Go to Actions > Docker Build and Push > Run workflow
```

---

### 3. Deploy Workflow (`deploy.yml`)

**Purpose:** Deploy to Railway (production/staging)

**Triggers:**
- Manual dispatch (recommended for production)
- Automatic after successful Docker build (optional)

**What it does:**
1. Installs Railway CLI
2. Links to Railway project
3. Deploys using `railway up`
4. Waits for deployment to complete
5. Runs health checks
6. Executes database migrations (if needed)
7. Generates deployment summary
8. Notifies on failure

**Requirements:**
- `RAILWAY_TOKEN` - Railway API token
- `RAILWAY_PROJECT_ID` - Railway project ID
- `RAILWAY_APP_URL` - Railway app URL for health checks

**How to use:**
```bash
# Manual deployment (recommended)
# 1. Go to Actions > Deploy to Railway
# 2. Click "Run workflow"
# 3. Select environment (production/staging)
# 4. Monitor deployment progress

# The workflow will:
# - Deploy latest Docker image
# - Run health checks
# - Update deployment status
```

---

## Setting Up Secrets

### Required GitHub Secrets

Navigate to: `Settings > Secrets and variables > Actions > New repository secret`

#### For Testing (test.yml):
```
GROQ_API_KEY
- Your Groq API key for running tests
- Get from: https://console.groq.com/
```

#### For Docker Build (docker-build.yml):
```
GITHUB_TOKEN
- Automatically provided by GitHub
- No action needed
```

#### For Deployment (deploy.yml):
```
RAILWAY_TOKEN
- Railway API token
- Get from: Railway Dashboard > Account Settings > Tokens

RAILWAY_PROJECT_ID
- Your Railway project ID
- Get from: Railway Dashboard > Project Settings

RAILWAY_APP_URL
- Your Railway app URL (e.g., https://smartsupport-ai.up.railway.app)
- Get from: Railway Dashboard > Deployments
```

---

## Status Badges

Add these badges to your README.md:

```markdown
![Tests](https://github.com/YOUR_USERNAME/REPO_NAME/actions/workflows/test.yml/badge.svg)
![Docker Build](https://github.com/YOUR_USERNAME/REPO_NAME/actions/workflows/docker-build.yml/badge.svg)
![Deploy](https://github.com/YOUR_USERNAME/REPO_NAME/actions/workflows/deploy.yml/badge.svg)
```

---

## Workflow Permissions

### Enable GitHub Actions:
1. Go to `Settings > Actions > General`
2. Under "Workflow permissions", select:
   - [DONE] Read and write permissions
   - [DONE] Allow GitHub Actions to create and approve pull requests

### Enable GitHub Packages:
1. Go to `Settings > Actions > General`
2. Scroll to "Workflow permissions"
3. Ensure packages have write access

---

## Troubleshooting

### Test Workflow Failing

**Issue:** Tests fail with import errors
```bash
# Solution: Check dependencies
pip install -r requirements.txt
pytest -v
```

**Issue:** Coverage below 70%
```bash
# Solution: Add more tests or adjust threshold in pytest.ini
# Temporarily: pytest --cov-fail-under=50
```

**Issue:** Flake8 linting errors
```bash
# Solution: Run locally and fix
flake8 src/
black src/
```

---

### Docker Build Failing

**Issue:** Authentication failed
```bash
# Solution: Check GitHub token permissions
# Ensure packages:write permission is enabled
```

**Issue:** Build timeout
```bash
# Solution: Optimize Dockerfile
# Use multi-stage builds
# Leverage caching
```

**Issue:** Image too large
```bash
# Solution: Use .dockerignore
# Minimize layers
# Use alpine-based images
```

---

### Deployment Failing

**Issue:** Railway token invalid
```bash
# Solution: Regenerate token
# Railway Dashboard > Account Settings > Tokens > Create Token
# Update GitHub secret
```

**Issue:** Health check failing
```bash
# Solution: Check app logs in Railway
# Verify GROQ_API_KEY is set in Railway
# Check /health endpoint locally
```

**Issue:** Database migration errors
```bash
# Solution: Run migrations manually
railway run python -m alembic upgrade head
```

---

## Local Testing

### Test the Test Workflow Locally
```bash
# Install dependencies
pip install -r requirements.txt

# Run linting
flake8 src/

# Check formatting
black --check src/

# Run tests with coverage
pytest --cov=src --cov-report=term-missing
```

### Test Docker Build Locally
```bash
# Build image
docker build -t smartsupport-ai:test .

# Run container
docker run -p 8000:8000 --env-file .env smartsupport-ai:test

# Test health endpoint
curl http://localhost:8000/health
```

### Test Deployment Locally
```bash
# Install Railway CLI
curl -fsSL https://railway.app/install.sh | sh

# Login
railway login

# Link project
railway link YOUR_PROJECT_ID

# Deploy
railway up
```

---

## Best Practices

1. **Always test locally before pushing**
   - Run tests: `pytest`
   - Check linting: `flake8 src/`
   - Format code: `black src/`

2. **Use meaningful commit messages**
   - Tests run on every push
   - Good commit messages help with debugging

3. **Monitor workflow runs**
   - Check Actions tab regularly
   - Fix failing workflows promptly

4. **Keep secrets secure**
   - Never commit secrets
   - Rotate tokens periodically
   - Use separate tokens for staging/production

5. **Review PRs before merging**
   - Ensure tests pass
   - Check coverage reports
   - Review code changes

6. **Use manual deployment for production**
   - Don't auto-deploy to production
   - Review changes before deploying
   - Have rollback plan ready

---

## Workflow Diagram

```
┌─────────────┐
│  Git Push   │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│   Test Workflow     │
│  - Lint             │
│  - Format Check     │
│  - Run Tests        │
│  - Coverage Report  │
└─────────┬───────────┘
          │
          ▼ (on main branch)
┌─────────────────────┐
│  Docker Build       │
│  - Build Image      │
│  - Push to GHCR     │
│  - Security Scan    │
└─────────┬───────────┘
          │
          ▼ (manual/auto)
┌─────────────────────┐
│   Deploy to Railway │
│  - Pull Image       │
│  - Deploy           │
│  - Health Check     │
│  - Migrations       │
└─────────────────────┘
```

---

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [Railway Documentation](https://docs.railway.app/)
- [pytest Documentation](https://docs.pytest.org/)
- [flake8 Documentation](https://flake8.pycqa.org/)

---

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review workflow logs in GitHub Actions
3. Check Railway logs for deployment issues
4. Create an issue in the repository
