# CI/CD Pipeline Setup Guide

Complete guide for setting up the Continuous Integration and Continuous Deployment pipeline for Multi-Agent HR Intelligence Platform.

## Overview

The CI/CD pipeline automates:
- **Testing:** Automated tests on every PR
- **Building:** Docker image creation and publishing
- **Deployment:** Automated deployment to Railway
- **Monitoring:** Health checks and notifications

## Architecture

```
Developer Push → GitHub → CI/CD Pipeline → Railway Production
                    ↓
              [Test] → [Build] → [Deploy]
                ↓         ↓          ↓
              Pass?    GHCR    Health Check
```

---

## Phase 1: Initial Setup

### 1. Enable GitHub Actions

1. Go to your repository on GitHub
2. Navigate to `Settings > Actions > General`
3. Under "Actions permissions", select:
   - [DONE] Allow all actions and reusable workflows
4. Under "Workflow permissions", select:
   - [DONE] Read and write permissions
   - [DONE] Allow GitHub Actions to create and approve pull requests
5. Click "Save"

### 2. Enable GitHub Packages

1. Go to `Settings > Actions > General`
2. Ensure "Workflow permissions" includes:
   - [DONE] Read and write permissions (for packages)

---

## Phase 2: Configure Secrets

### GitHub Repository Secrets

Navigate to: `Settings > Secrets and variables > Actions`

#### Required Secrets:

1. **GROQ_API_KEY**
   ```
   Description: Groq API key for AI operations
   Where to get: https://console.groq.com/
   Used by: test.yml
   ```

2. **RAILWAY_TOKEN**
   ```
   Description: Railway API token for deployment
   Where to get: Railway Dashboard > Account Settings > Tokens
   Used by: deploy.yml
   ```

3. **RAILWAY_PROJECT_ID**
   ```
   Description: Railway project identifier
   Where to get: Railway Dashboard > Project Settings
   Used by: deploy.yml
   ```

4. **RAILWAY_APP_URL**
   ```
   Description: Railway application URL
   Example: https://smartsupport-ai.up.railway.app
   Used by: deploy.yml (health checks)
   ```

### How to Add Secrets:

```bash
# Step 1: Click "New repository secret"
# Step 2: Enter name (e.g., GROQ_API_KEY)
# Step 3: Paste value
# Step 4: Click "Add secret"
# Step 5: Repeat for each secret
```

---

## Phase 3: Workflow Files

### Files Created:

```
.github/workflows/
├── test.yml           # Automated testing
├── docker-build.yml   # Docker image building
├── deploy.yml         # Railway deployment
└── README.md          # Workflow documentation

Configuration files:
├── pytest.ini         # Pytest configuration
├── .flake8           # Linting rules
└── requirements.txt   # Updated with testing deps
```

---

## Phase 4: Workflow Details

### 1. Test Workflow (test.yml)

**Triggers:**
- Pull requests to `main`
- Pushes to `main` and `develop`

**Steps:**
1. Checkout code
2. Setup Python 3.10 with pip caching
3. Install dependencies
4. Lint with flake8 (syntax errors fail build)
5. Check formatting with black
6. Run pytest with coverage (70% minimum)
7. Upload coverage to Codecov
8. Generate test summary

**Status:** [DONE] Blocks PRs if tests fail

**Example output:**
```
[OK] Checkout code
[OK] Setup Python 3.10
[OK] Install dependencies
[OK] Lint with flake8 (0 errors)
[OK] Check formatting (passed)
[OK] Run tests (100% passed, coverage 85%)
[OK] Upload coverage
```

---

### 2. Docker Build Workflow (docker-build.yml)

**Triggers:**
- Push to `main` branch
- Release creation
- Manual dispatch

**Steps:**
1. Checkout repository
2. Setup Docker Buildx (multi-platform)
3. Login to GitHub Container Registry
4. Extract metadata (tags/labels)
5. Build Docker image with caching
6. Push to `ghcr.io/YOUR_USERNAME/smartsupport-ai`
7. Run health check on image
8. Scan for vulnerabilities (Trivy)

**Image Tags:**
- `latest` - Latest main branch
- `v1.0.0` - Release versions
- `main-abc1234` - Commit SHA
- `staging` - Staging branch

**Registry:** `ghcr.io/YOUR_USERNAME/smartsupport-ai`

**Example output:**
```
[OK] Build image (2m 30s)
[OK] Push to registry
[OK] Tagged: latest, main-abc1234
[OK] Security scan (0 critical, 2 medium)
```

---

### 3. Deploy Workflow (deploy.yml)

**Triggers:**
- Manual dispatch (recommended)
- After successful Docker build (optional)

**Steps:**
1. Install Railway CLI
2. Link to Railway project
3. Deploy with `railway up`
4. Wait for deployment (60s)
5. Run health checks (10 attempts)
6. Execute database migrations
7. Generate deployment summary
8. Notify on failure

**Environments:**
- Production (default)
- Staging (optional)

**Example output:**
```
[OK] Install Railway CLI
[OK] Deploy to Railway
[OK] Health check (200 OK)
[OK] Database migrations (0 pending)
[OK] Deployment successful
```

---

## Phase 5: Testing Configuration

### pytest.ini

```ini
[pytest]
testpaths = tests, src
addopts = -v --showlocals -ra --cov-fail-under=70
markers =
    slow: slow tests
    integration: integration tests
    unit: unit tests
    requires_groq: needs API key
```

**Features:**
- Verbose output
- Coverage threshold: 70%
- Test markers for categorization
- Asyncio support

### .flake8

```ini
[flake8]
max-line-length = 120
max-complexity = 15
ignore = E501, W503, E203, F401
exclude = .git, __pycache__, venv, data
```

**Features:**
- Line length: 120 characters
- Complexity limit: 15
- Black-compatible
- Excludes common directories

---

## Phase 6: Usage Guide

### For Developers

#### Before Pushing Code:
```bash
# 1. Run tests locally
pytest

# 2. Check linting
flake8 src/

# 3. Format code
black src/

# 4. Commit and push
git add .
git commit -m "feat: add new feature"
git push
```

#### Creating a Pull Request:
```bash
# 1. Create feature branch
git checkout -b feature/new-feature

# 2. Make changes and commit
git add .
git commit -m "feat: implement feature"

# 3. Push branch
git push origin feature/new-feature

# 4. Create PR on GitHub
# - Tests will run automatically
# - PR blocked if tests fail
# - Merge after review and passing tests
```

---

### For Maintainers

#### Manual Deployment:
```bash
# 1. Go to GitHub Actions
# 2. Select "Deploy to Railway"
# 3. Click "Run workflow"
# 4. Choose environment (production/staging)
# 5. Monitor progress
# 6. Verify deployment
```

#### Checking Workflow Status:
```bash
# Via GitHub UI:
# - Go to Actions tab
# - View recent workflow runs
# - Check logs for failures

# Via CLI (gh CLI tool):
gh workflow list
gh run list
gh run view <run-id>
```

#### Manual Docker Build:
```bash
# 1. Go to Actions > Docker Build and Push
# 2. Click "Run workflow"
# 3. Select branch (main)
# 4. Monitor build progress
# 5. Verify image pushed to GHCR
```

---

## Phase 7: Monitoring & Maintenance

### Status Badges

Add to README.md:

```markdown
# Multi-Agent HR Intelligence Platform

![Tests](https://github.com/YOUR_USERNAME/smartsupport-ai/actions/workflows/test.yml/badge.svg)
![Docker](https://github.com/YOUR_USERNAME/smartsupport-ai/actions/workflows/docker-build.yml/badge.svg)
![Deploy](https://github.com/YOUR_USERNAME/smartsupport-ai/actions/workflows/deploy.yml/badge.svg)
[![Coverage](https://codecov.io/gh/YOUR_USERNAME/smartsupport-ai/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/smartsupport-ai)
```

### Monitoring Checklist:

- [ ] Check Actions tab daily
- [ ] Review failed workflows
- [ ] Monitor deployment health
- [ ] Check coverage trends
- [ ] Review security scan results
- [ ] Update dependencies monthly

---

## Phase 8: Troubleshooting

### Common Issues

#### 1. Test Workflow Failing

**Issue:** Import errors
```bash
Solution:
1. Check requirements.txt
2. Verify Python version (3.10)
3. Clear cache: Delete .pytest_cache
```

**Issue:** Coverage below 70%
```bash
Solution:
1. Add more tests
2. Remove untested code
3. Adjust threshold in pytest.ini
```

**Issue:** Flake8 errors
```bash
Solution:
1. Run: flake8 src/ --show-source
2. Fix syntax errors
3. Format: black src/
4. Commit and push
```

---

#### 2. Docker Build Failing

**Issue:** Authentication failed
```bash
Solution:
1. Check GITHUB_TOKEN permissions
2. Settings > Actions > Workflow permissions
3. Enable "Read and write permissions"
```

**Issue:** Build timeout
```bash
Solution:
1. Optimize Dockerfile (multi-stage builds)
2. Use .dockerignore
3. Leverage build cache
```

**Issue:** Image size too large
```bash
Solution:
1. Use alpine-based images
2. Minimize layers
3. Clean up after apt-get
4. Use .dockerignore effectively
```

---

#### 3. Deployment Failing

**Issue:** Railway token invalid
```bash
Solution:
1. Generate new token in Railway
2. Update RAILWAY_TOKEN secret
3. Re-run workflow
```

**Issue:** Health check failing
```bash
Solution:
1. Check Railway logs
2. Verify environment variables
3. Check /health endpoint
4. Increase timeout in deploy.yml
```

**Issue:** Database migration errors
```bash
Solution:
1. SSH to Railway: railway run bash
2. Run manually: alembic upgrade head
3. Check migration scripts
4. Verify database connection
```

---

## Phase 9: Security Best Practices

### Secrets Management:

1. **Never commit secrets**
   ```bash
   # Check before committing
   git diff
   grep -r "GROQ_API_KEY" .
   ```

2. **Rotate secrets regularly**
   ```bash
   # Every 90 days:
   - Generate new API keys
   - Update GitHub secrets
   - Update Railway environment
   ```

3. **Use separate environments**
   ```bash
   # Development: Local .env
   # Staging: Railway staging
   # Production: Railway production
   ```

4. **Limit secret scope**
   ```bash
   # Only grant necessary permissions
   # Use read-only tokens when possible
   # Monitor secret usage
   ```

### Dependency Security:

1. **Dependabot alerts**
   ```bash
   # Enable: Settings > Security > Dependabot
   # Review alerts weekly
   # Update vulnerable dependencies
   ```

2. **Security scanning**
   ```bash
   # Trivy scans in docker-build.yml
   # Review scan results
   # Fix critical/high vulnerabilities
   ```

---

## Phase 10: Advanced Configuration

### Conditional Workflows

**Run only on specific paths:**
```yaml
on:
  push:
    paths:
      - 'src/**'
      - 'tests/**'
```

**Skip workflows:**
```bash
# In commit message:
git commit -m "docs: update README [skip ci]"
```

### Environment Protection

**Add deployment approval:**
```bash
# Settings > Environments > production
# Add required reviewers
# Set branch protection rules
```

### Notifications

**Slack integration:**
```yaml
- name: Notify Slack
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK }}
```

**Email notifications:**
```bash
# Settings > Notifications
# Enable workflow notifications
```

---

## Phase 11: Performance Optimization

### Caching Strategies:

1. **Pip dependencies:**
   ```yaml
   - uses: actions/setup-python@v5
     with:
       cache: 'pip'
   ```

2. **Docker layers:**
   ```yaml
   - uses: docker/build-push-action@v5
     with:
       cache-from: type=registry,ref=...
       cache-to: type=registry,ref=...
   ```

3. **Test results:**
   ```yaml
   - uses: actions/cache@v3
     with:
       path: .pytest_cache
   ```

### Parallel Jobs:

```yaml
strategy:
  matrix:
    python-version: ["3.9", "3.10", "3.11"]
  max-parallel: 3
```

---

## Phase 12: Next Steps

### Immediate Actions:

1. [DONE] Review workflow files
2. [DONE] Add GitHub secrets
3. [DONE] Test workflows locally
4. [DONE] Push to GitHub
5. [DONE] Monitor first run
6. [DONE] Fix any issues
7. [DONE] Document team procedures

### Future Enhancements:

- [ ] Add integration tests
- [ ] Implement blue-green deployment
- [ ] Add performance testing
- [ ] Set up staging environment
- [ ] Add Slack notifications
- [ ] Implement automatic rollback
- [ ] Add load testing
- [ ] Set up monitoring dashboard

---

## Quick Reference

### Workflow Commands:

```bash
# Trigger manual workflow
gh workflow run deploy.yml

# View workflow runs
gh run list --workflow=test.yml

# Watch workflow run
gh run watch

# View logs
gh run view <run-id> --log

# Re-run failed jobs
gh run rerun <run-id>
```

### Docker Commands:

```bash
# Pull latest image
docker pull ghcr.io/YOUR_USERNAME/smartsupport-ai:latest

# Run locally
docker run -p 8000:8000 \
  -e GROQ_API_KEY=$GROQ_API_KEY \
  ghcr.io/YOUR_USERNAME/smartsupport-ai:latest

# Check health
curl http://localhost:8000/health
```

### Railway Commands:

```bash
# Deploy manually
railway up

# View logs
railway logs

# Run command
railway run python -m pytest

# SSH to container
railway run bash
```

---

## Support & Resources

### Documentation:
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [Railway Docs](https://docs.railway.app/)

### Internal Docs:
- `.github/workflows/README.md` - Detailed workflow documentation
- `DOCKER_README.md` - Docker setup guide
- `PHASE_3_DOCKER_COMPLETE.md` - Docker phase completion

### Getting Help:
1. Check troubleshooting section
2. Review workflow logs
3. Check Railway logs
4. Create GitHub issue
5. Contact team lead

---

## Success Metrics

### CI/CD Health:

- **Test Pass Rate:** > 95%
- **Build Success Rate:** > 98%
- **Deployment Success Rate:** > 95%
- **Average Build Time:** < 5 minutes
- **Average Test Time:** < 3 minutes
- **Coverage:** > 70%

### Monitor These:

```bash
# Weekly review:
- Failed workflow count
- Average build duration
- Test coverage trend
- Security scan results
- Deployment frequency
- Mean time to recovery (MTTR)
```

---

## Conclusion

Your CI/CD pipeline is now complete with:

[DONE] Automated testing on every PR
[DONE] Docker image building and publishing
[DONE] Railway deployment (manual/automated)
[DONE] Health checks and monitoring
[DONE] Security scanning
[DONE] Coverage reporting
[DONE] Comprehensive documentation

**Next Phase:** Railway deployment configuration and production readiness

---

**Created:** 2024
**Last Updated:** 2024
**Version:** 1.0.0
**Status:** [DONE] Production Ready
