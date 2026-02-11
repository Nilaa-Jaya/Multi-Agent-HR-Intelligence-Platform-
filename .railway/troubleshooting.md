# Railway Deployment Troubleshooting Guide

Common issues and solutions for Railway deployment of Multi-Agent HR Intelligence Platform.

---

## Table of Contents

1. [Build Failures](#build-failures)
2. [Deployment Failures](#deployment-failures)
3. [Database Issues](#database-issues)
4. [Environment Variable Issues](#environment-variable-issues)
5. [Application Errors](#application-errors)
6. [Performance Issues](#performance-issues)
7. [Logging & Debugging](#logging--debugging)

---

## Build Failures

### Issue: pip install fails

**Symptoms:**
```
ERROR: Could not find a version that satisfies the requirement...
```

**Solutions:**
1. Check `requirements.txt` format:
   ```bash
   # Ensure no extra spaces or special characters
   # Use exact versions: package==version
   ```

2. Verify Python version compatibility:
   ```json
   // In railway.json
   "environments": {
     "production": {
       "variables": {
         "PYTHON_VERSION": "3.10"
       }
     }
   }
   ```

3. Check for conflicting dependencies:
   ```bash
   pip install -r requirements.txt
   # Run locally first to verify
   ```

---

### Issue: Build timeout

**Symptoms:**
```
Build exceeded maximum time limit
```

**Solutions:**
1. Optimize requirements.txt (remove unused packages)
2. Use build cache:
   ```bash
   # Railway automatically caches, but verify in logs
   ```
3. Contact Railway support for timeout increase

---

## Deployment Failures

### Issue: Application won't start

**Symptoms:**
```
Application failed to respond to health checks
```

**Solutions:**

1. **Check start command in railway.json:**
   ```json
   {
     "deploy": {
       "startCommand": "gunicorn src.api.app:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT"
     }
   }
   ```

2. **Verify PORT variable:**
   ```bash
   railway vars
   # Ensure PORT is set (Railway sets this automatically)
   ```

3. **Check application binds to correct port:**
   ```python
   # In src/api/app.py, ensure using settings.port or PORT env var
   port = int(os.getenv("PORT", 8000))
   ```

---

### Issue: Health check failing

**Symptoms:**
```
Health check timeout at /api/v1/health
```

**Solutions:**

1. **Verify health endpoint exists:**
   ```bash
   curl https://your-app.up.railway.app/api/v1/health
   ```

2. **Check health check configuration:**
   ```json
   {
     "deploy": {
       "healthcheckPath": "/api/v1/health",
       "healthcheckTimeout": 100
     }
   }
   ```

3. **Increase timeout if app is slow to start:**
   ```json
   "healthcheckTimeout": 200
   ```

4. **Check logs for errors:**
   ```bash
   railway logs
   ```

---

## Database Issues

### Issue: Database connection failed

**Symptoms:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solutions:**

1. **Verify DATABASE_URL is set:**
   ```bash
   railway vars | grep DATABASE_URL
   # Should show PostgreSQL connection string
   ```

2. **Check PostgreSQL service is running:**
   - Go to Railway dashboard
   - Verify PostgreSQL service status is "Active"

3. **Enable SSL connection:**
   ```python
   # In src/database/connection.py
   connect_args = {"sslmode": "require"}
   ```

4. **Check database credentials:**
   ```bash
   railway run bash
   echo $DATABASE_URL
   # Verify format: postgresql://user:pass@host:port/db
   ```

---

### Issue: Tables not created

**Symptoms:**
```
Table 'conversations' doesn't exist
```

**Solutions:**

1. **Run initialization script manually:**
   ```bash
   railway run python scripts/railway_init.py
   ```

2. **Check if init ran during deployment:**
   ```bash
   railway logs | grep "Database initialized"
   ```

3. **Verify models are imported:**
   ```python
   # In src/database/models.py
   # Ensure all models inherit from Base
   ```

4. **Run migrations manually:**
   ```bash
   railway run python -c "from src.database.connection import init_db; init_db()"
   ```

---

### Issue: Database connection pool exhausted

**Symptoms:**
```
QueuePool limit of size 10 overflow 20 reached
```

**Solutions:**

1. **Increase pool size:**
   ```python
   # In src/database/connection.py
   engine = create_engine(
       settings.database_url,
       pool_size=20,  # Increase from 10
       max_overflow=40  # Increase from 20
   )
   ```

2. **Enable connection recycling:**
   ```python
   pool_recycle=3600  # Recycle connections after 1 hour
   ```

3. **Check for connection leaks:**
   ```python
   # Ensure all db sessions are closed
   try:
       db = next(get_db())
       # ... operations
   finally:
       db.close()
   ```

---

## Environment Variable Issues

### Issue: GROQ_API_KEY not found

**Symptoms:**
```
KeyError: 'GROQ_API_KEY'
ValidationError: field required
```

**Solutions:**

1. **Add variable in Railway:**
   - Dashboard → Variables → Raw Editor
   - Add: `GROQ_API_KEY=your_key_here`

2. **Verify variable is set:**
   ```bash
   railway vars | grep GROQ_API_KEY
   ```

3. **Restart deployment:**
   ```bash
   railway restart
   ```

4. **Check variable name spelling:**
   - Must be exactly: `GROQ_API_KEY`
   - Check for extra spaces or typos

---

### Issue: Variables not updating

**Symptoms:**
- Changed variable but app still uses old value

**Solutions:**

1. **Redeploy after variable change:**
   ```bash
   railway restart
   # Or trigger new deployment
   ```

2. **Clear Railway cache:**
   - Settings → Clear Cache → Redeploy

3. **Check variable scope:**
   - Ensure variables are in correct environment (production)

---

## Application Errors

### Issue: 500 Internal Server Error

**Symptoms:**
```
HTTP 500 when making API requests
```

**Solutions:**

1. **Check application logs:**
   ```bash
   railway logs --tail 100
   ```

2. **Enable debug logging:**
   ```bash
   # Add environment variable
   LOG_LEVEL=DEBUG
   ```

3. **Test locally with same environment:**
   ```bash
   # Copy Railway DATABASE_URL
   export DATABASE_URL="postgresql://..."
   export GROQ_API_KEY="..."
   python -m src.api.app
   ```

4. **Check for missing dependencies:**
   ```bash
   railway run pip freeze | grep <package-name>
   ```

---

### Issue: Slow response times

**Symptoms:**
- Requests take >10 seconds
- Timeout errors

**Solutions:**

1. **Increase worker count:**
   ```json
   // In Procfile or railway.json
   --workers 6  // Increase from 4
   ```

2. **Optimize database queries:**
   ```python
   # Add indexes, use eager loading
   db.query(Model).options(joinedload(Model.relationship))
   ```

3. **Enable caching:**
   ```python
   # Use Redis for caching if needed
   ```

4. **Check Groq API latency:**
   ```bash
   # May be external API issue
   curl -w "@curl-format.txt" -o /dev/null -s https://api.groq.com/...
   ```

---

### Issue: Memory limit exceeded

**Symptoms:**
```
Container exceeded memory limit
```

**Solutions:**

1. **Reduce worker count:**
   ```
   --workers 2  # Reduce from 4
   ```

2. **Upgrade Railway plan:**
   - Hobby: 512MB RAM
   - Pro: 8GB RAM

3. **Optimize memory usage:**
   ```python
   # Use generators instead of lists
   # Clear large objects after use
   # del large_object
   ```

4. **Monitor memory usage:**
   ```bash
   railway run ps aux
   ```

---

## Performance Issues

### Issue: High latency

**Symptoms:**
- API responses slow
- Users experiencing delays

**Solutions:**

1. **Add database connection pooling:**
   ```python
   pool_pre_ping=True  # Verify connections
   ```

2. **Enable query caching:**
   ```python
   @lru_cache(maxsize=100)
   def get_cached_data(...):
   ```

3. **Use CDN for static assets:**
   - Railway auto-provides CDN

4. **Profile slow endpoints:**
   ```python
   import cProfile
   cProfile.run('slow_function()')
   ```

---

### Issue: Database queries slow

**Symptoms:**
- Queries taking >1 second

**Solutions:**

1. **Add database indexes:**
   ```sql
   CREATE INDEX idx_user_id ON conversations(user_id);
   ```

2. **Analyze query plans:**
   ```python
   from sqlalchemy import inspect
   print(query.statement.compile(compile_kwargs={"literal_binds": True}))
   ```

3. **Use database monitoring:**
   - Railway → Database → Metrics

---

## Logging & Debugging

### Access logs

```bash
# Real-time logs
railway logs --tail

# Last 100 lines
railway logs --tail 100

# Filter by keyword
railway logs | grep ERROR

# Deployment logs only
railway logs --deployment <deployment-id>
```

---

### Debug in production

```bash
# SSH into running container
railway run bash

# Check environment
railway run env

# Test database connection
railway run python -c "from src.database.connection import get_db; db=next(get_db()); print('DB OK')"

# Test API endpoints
railway run curl http://localhost:$PORT/api/v1/health
```

---

### Check service metrics

```bash
# View metrics
railway status

# Check resource usage
railway metrics

# View builds
railway builds
```

---

## Common Error Messages

### "ModuleNotFoundError: No module named 'src'"

**Solution:**
```bash
# Ensure PYTHONPATH is set correctly
export PYTHONPATH="${PYTHONPATH}:."

# Or use python -m
python -m src.api.app
```

---

### "Port already in use"

**Solution:**
```bash
# Railway sets PORT automatically
# Don't hardcode port 8000

# Use environment variable
port = int(os.getenv("PORT", 8000))
```

---

### "SSL SYSCALL error: EOF detected"

**Solution:**
```python
# PostgreSQL connection issue
# Enable SSL and connection retries

connect_args = {
    "sslmode": "require",
    "connect_timeout": 10
}
```

---

## Emergency Procedures

### Rollback to previous deployment

```bash
# View deployments
railway deployments

# Rollback to specific deployment
railway rollback <deployment-id>
```

---

### Database restore

```bash
# Railway automatic backups
# Go to: Database Service → Backups → Restore

# Manual backup
railway run pg_dump $DATABASE_URL > backup.sql

# Manual restore
railway run psql $DATABASE_URL < backup.sql
```

---

### Force restart

```bash
# Restart service
railway restart

# Redeploy from scratch
railway up --detach

# Clear all caches
# Settings → Clear Cache → Redeploy
```

---

## Getting Help

### Railway Support

1. **Documentation:** https://docs.railway.app/
2. **Discord:** https://discord.gg/railway
3. **Status Page:** https://status.railway.app/
4. **Email:** team@railway.app

### Project-Specific

1. **GitHub Issues:** Create issue in repository
2. **Check logs:** `railway logs --tail 500`
3. **Review recent changes:** `git log --oneline -10`
4. **Test locally:** Replicate environment locally

---

## Preventive Measures

### Pre-deployment checks

- [ ] Test locally with production DATABASE_URL
- [ ] Run full test suite
- [ ] Check all environment variables
- [ ] Review recent code changes
- [ ] Verify dependencies are up to date

### Monitoring

- [ ] Set up uptime monitoring
- [ ] Enable error tracking (Sentry)
- [ ] Monitor resource usage
- [ ] Set up alerts for failures
- [ ] Regular log reviews

---

**Last Updated:** 2024-11-24
**Version:** 1.0.0

For additional help, see `RAILWAY_DEPLOYMENT.md` for full deployment guide.
